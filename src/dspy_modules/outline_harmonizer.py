"""
DSPy module for harmonizing multiple course outlines into a single consolidated curriculum
following a configurable Standard Engineering Course Template.
"""
import dspy
import yaml
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# --- 0. Load Template Configuration ---

def load_curriculum_template() -> List[Dict]:
    """Load the curriculum template from YAML config."""
    config_path = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', 'config', 'curriculum_template.yaml'
    )
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('modules', [])
    except FileNotFoundError:
        print(f"[WARN] Template config not found at {config_path}, using defaults")
        return []

TEMPLATE_MODULES = load_curriculum_template()

def build_dynamic_prompt() -> str:
    """Build the LLM prompt dynamically from YAML config."""
    if not TEMPLATE_MODULES:
        return "You are an expert Instructional Designer. Create a unified course structure."
    
    # Build numbered list and JSON structure
    numbered_list = []
    json_structure = {}
    
    for i, module in enumerate(TEMPLATE_MODULES):
        key = module['key']
        is_list = module.get('is_list', False)
        desc = module.get('description', '')
        
        # For list modules, use description; for single modules, use title
        if is_list:
            display_name = desc.split('.')[0] if desc else key.replace('_', ' ').title()
        else:
            display_name = module.get('title') or key.replace('_', ' ').title()
        
        numbered_list.append(f"{i+1}. {display_name}")
        
        if is_list:
            json_structure[key] = '[{"title": "...", "rationale": "...", "key_concepts": [...]}]'
        else:
            json_structure[key] = '{"title": "...", "rationale": "...", "key_concepts": [...]}'
    
    prompt = f"""You are an expert Instructional Designer for Engineering.
Given outlines from multiple business units, create a Unified Standard Course.

You MUST follow this template:
{chr(10).join(numbered_list)}

Output as JSON matching this structure:
{{
{chr(10).join([f'  "{k}": {v},' for k, v in json_structure.items()])[:-1]}
}}

CRITICAL INSTRUCTIONS FOR MISSING CONTENT:
1. You MUST include ALL standard modules even if source material is missing.
2. If source material does NOT contain concepts relevant to a module:
   - Create the module in the JSON.
   - Set 'key_concepts' to an EMPTY LIST [].
   - Set 'rationale' to "NO_SOURCE_DATA".
3. DO NOT invent or hallucinate concepts. Only use concepts derived from input.
4. For technical_modules, create MULTIPLE sections by merging and de-duplicating source topics into a logical flow (Fundamentals -> Advanced).
"""
    
    return prompt

# --- 1. Input Models ---

class SourceOutline(BaseModel):
    """A section from a source course"""
    bu: str = Field(description="Business unit this section is from")
    section_title: str = Field(description="Title of the section")
    concepts: List[str] = Field(description="Key concepts taught in this section")

# --- 2. Output Models ---

class TargetSection(BaseModel):
    """A proposed section in the consolidated curriculum"""
    title: str = Field(description="Title for the target section")
    rationale: str = Field(description="Why this section is needed")
    key_concepts: List[str] = Field(description="Top 3-5 concepts to teach")

# --- 3. The Signature ---

class GenerateConsolidatedSkeleton(dspy.Signature):
    __doc__ = build_dynamic_prompt()
    
    # Input: Raw string representation of the source JSON
    source_outlines: str = dspy.InputField(
        desc="JSON list of source sections with BU, title, and concepts"
    )
    
    # Output: JSON string matching StandardCoursePlan structure
    consolidated_plan: str = dspy.OutputField(
        desc="JSON object matching the template structure"
    )


# --- 4. The Module ---

class OutlineHarmonizer(dspy.Module):
    """Module that harmonizes outlines into a Standard Template"""
    
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(GenerateConsolidatedSkeleton)
        self.template_modules = TEMPLATE_MODULES
    
    def forward(self, source_outlines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Args:
            source_outlines: List of dicts from Neo4j (BU, Section, Concepts)
            
        Returns:
            List of dicts (The flattened tree structure for the UI)
        """
        import json
        
        # 1. Prepare Input
        source_json_str = json.dumps(source_outlines, indent=2)
        
        # 2. Call DSPy
        prediction = self.generate(source_outlines=source_json_str)
        
        print(f"\n{'='*60}")
        print("[DEBUG] Raw LLM Response:")
        print(prediction.consolidated_plan)
        print(f"{'='*60}\n")
        
        # 3. Parse the JSON output
        try:
            plan_data = json.loads(prediction.consolidated_plan)
            
            if not isinstance(plan_data, dict):
                raise ValueError("Expected dict for StandardCoursePlan")
            
            # 4. Flatten to List using YAML config order
            final_tree = []
            
            for module_config in self.template_modules:
                key = module_config['key']
                module_type = module_config.get('type', 'technical')
                is_list = module_config.get('is_list', False)
                
                if key in plan_data:
                    if is_list and isinstance(plan_data[key], list):
                        for item in plan_data[key]:
                            item['type'] = module_type
                            final_tree.append(item)
                    else:
                        section_dict = plan_data[key]
                        section_dict['type'] = module_type
                        final_tree.append(section_dict)
            
            print(f"[DEBUG] Generated standard course with {len(final_tree)} modules")
            return final_tree
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"[WARN] Failed to parse StandardCoursePlan: {e}")
            print(f"[WARN] Raw LLM output: {prediction.consolidated_plan}")
            
            # Fallback: Try to parse as a simple list (old format)
            try:
                sections_list = json.loads(prediction.consolidated_plan)
                if isinstance(sections_list, list):
                    for s in sections_list:
                        if 'type' not in s:
                            s['type'] = 'technical'
                    return sections_list
            except:
                pass
            
            print("[ERROR] Using fallback: returning source outlines")
            return self._fallback_merge(source_outlines)
    
    def _fallback_merge(self, source_outlines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Emergency fallback if DSPy fails completely"""
        sections = []
        for source in source_outlines:
            sections.append({
                "title": source['section_title'],
                "rationale": f"Based on content from {source['bu']}",
                "key_concepts": source['concepts'][:5],
                "type": "technical"
            })
        return sections