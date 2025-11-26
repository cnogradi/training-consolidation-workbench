import React, { useEffect, useState } from 'react';
import { Plus, Sparkles, GitMerge } from 'lucide-react';
import { useDroppable } from '@dnd-kit/core';
import { useSortable, SortableContext, verticalListSortingStrategy, arrayMove } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { api } from '../api';
import type { TargetDraftNode } from '../api';
import clsx from 'clsx';

interface ConsolidationCanvasProps {
    projectId: string | null;
    setProjectId: (id: string) => void;
    discipline: string;
    refreshTrigger?: number;
}

export const ConsolidationCanvas: React.FC<ConsolidationCanvasProps> = ({ projectId, setProjectId, discipline, refreshTrigger }) => {
    const [structure, setStructure] = useState<TargetDraftNode[]>([]);
    // const [loading, setLoading] = useState(false);

    // Initial Project Creation if needed
    useEffect(() => {
        if (!projectId) {
            // Auto-create for demo
            api.createDraftProject(`Unified ${discipline} Standard`).then(p => {
                setProjectId(p.id);
                // Add a default chapter
                api.addDraftNode(p.id, "Topic 1").then(() => {
                    fetchStructure(p.id);
                });
            });
        } else {
            fetchStructure(projectId);
        }
    }, [projectId, discipline, refreshTrigger]);

    const fetchStructure = async (pid: string) => {
        const nodes = await api.getDraftStructure(pid);
        setStructure(nodes);
    };

    // Identify the current active drop target (usually the last added node or specific one)
    // For simplicity, we'll make the whole "Topic 1" card droppable.
    // We need to know which node is the target.
    // Let's find the first child node to be the target for now.
    // const targetNode = structure.find(n => n.parent_id === projectId) || structure[0];

    return (
        <div className="flex-1 bg-slate-50 p-6 flex flex-col h-full overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-brand-teal" />
                    <h2 className="font-bold text-slate-800">Consolidated Outline</h2>
                </div>
                <button className="text-brand-teal hover:bg-brand-teal/10 p-1 rounded">
                    <Plus size={20} />
                </button>
            </div>

            {/* Canvas Area */}
            <div className="max-w-3xl mx-auto w-full space-y-6 pb-20">
                {/* Root Project Title */}
                <div className="text-center mb-8">
                    <h1 className="text-2xl font-bold text-slate-800">
                        {structure.find(n => n.id === projectId)?.title || "Loading..."}
                    </h1>
                    <p className="text-slate-500 text-sm">Start building your consolidated outline...</p>
                </div>

                {/* Draft Nodes */}
                {structure.filter(n => n.parent_id === projectId).map(node => (
                    <DraftNodeCard key={node.id} node={node} onRefresh={() => fetchStructure(projectId!)} />
                ))}

                {/* Empty State / Placeholder */}
                {structure.length <= 1 && (
                    <div className="border-2 border-dashed border-slate-200 rounded-xl p-12 flex flex-col items-center justify-center text-slate-400">
                        <GitMerge size={48} className="mb-4 opacity-20" />
                        <p>Ready to Consolidate</p>
                        <p className="text-sm">Drag legacy policies from the left to synthesize.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

const SortableSlideThumbnail: React.FC<{ id: string, url?: string }> = ({ id, url }) => {
    const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });
    
    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
    };

    return (
        <div 
            ref={setNodeRef} 
            style={style} 
            {...attributes} 
            {...listeners}
            className="w-full h-16 bg-white border border-slate-200 rounded flex items-center gap-3 p-2 shadow-sm cursor-grab active:cursor-grabbing hover:border-brand-teal hover:shadow-md transition-all"
        >
            <div className="w-16 h-12 bg-slate-100 rounded overflow-hidden flex-shrink-0 border border-slate-100">
                {url ? (
                    <img src={url} alt="Thumbnail" className="w-full h-full object-cover" />
                ) : (
                    <div className="w-full h-full flex items-center justify-center text-[10px] text-slate-400">
                        No Img
                    </div>
                )}
            </div>
            <div className="flex-1 flex flex-col justify-center">
                <span className="text-xs font-medium text-slate-700">Slide {id.split('_p')[1] || '?'}</span>
                <span className="text-[10px] text-slate-400 truncate">{id}</span>
            </div>
            <div className="text-slate-300 pr-2">
                {/* Grip icon placeholder */}
                <div className="flex flex-col gap-[2px]">
                    <div className="w-1 h-1 bg-current rounded-full"/>
                    <div className="w-1 h-1 bg-current rounded-full"/>
                    <div className="w-1 h-1 bg-current rounded-full"/>
                </div>
            </div>
        </div>
    );
};

const DraftNodeCard: React.FC<{ node: TargetDraftNode, onRefresh: () => void }> = ({ node, onRefresh }) => {
    const { isOver, setNodeRef } = useDroppable({
        id: node.id,
        data: { type: 'target', node }
    });
    
    // Local state for immediate reordering feedback
    const [items, setItems] = useState(node.source_refs);

    // Update items if node.source_refs changes (e.g. from backend refresh)
    useEffect(() => {
        // Only update if length differs to allow local reordering to persist visually?
        // Or simple sync.
        // Let's simple sync but this will revert reordering if refreshed.
        // Since backend doesn't support order, we must maintain it locally or just let it be transient.
        // But we want immediate feedback.
        if (JSON.stringify(items) !== JSON.stringify(node.source_refs)) {
             // If they differ only in order, we might want to keep local order?
             // For now, sync.
             setItems(node.source_refs);
        }
    }, [node.source_refs]);

    useEffect(() => {
        const handleReorder = (e: Event) => {
            const event = e as CustomEvent;
            const { activeId, overId } = event.detail;
            
            if (items.includes(activeId) && items.includes(overId)) {
                const oldIndex = items.indexOf(activeId);
                const newIndex = items.indexOf(overId);
                
                if (oldIndex !== -1 && newIndex !== -1) {
                    setItems((items) => arrayMove(items, oldIndex, newIndex));
                }
            }
        };
        
        window.addEventListener('slide-reorder', handleReorder);
        return () => window.removeEventListener('slide-reorder', handleReorder);
    }, [items]);
    
    const [synthesizing, setSynthesizing] = useState(false);
    const [preview, setPreview] = useState(node.content_markdown);

    // We need to keep structure in sync with preview state when refreshed
    // But for now, simple update
    useEffect(() => {
        if (node.content_markdown) {
            setPreview(node.content_markdown);
        }
    }, [node.content_markdown]);

    const [thumbnails, setThumbnails] = useState<Record<string, string>>({});

    useEffect(() => {
        const loadThumbnails = async () => {
            const thumbs: Record<string, string> = {};
            for (const refId of items) {
                try {
                    const details = await api.getSlideDetails(refId);
                    thumbs[refId] = details.s3_url;
                } catch (e) {
                    console.error("Failed to load thumb", e);
                }
            }
            setThumbnails(thumbs);
        };
        
        if (items.length > 0) {
            loadThumbnails();
        }
    }, [items]);

    const handleSynthesize = async () => {
        setSynthesizing(true);
        try {
            await api.triggerSynthesis(node.id, "Professional standard");
            // Start polling
            const poll = setInterval(async () => {
                const status = await api.getSynthesisPreview(node.id);
                if (status.status === 'complete' || status.content) {
                    setPreview(status.content);
                    setSynthesizing(false);
                    clearInterval(poll);
                    onRefresh();
                }
            }, 2000);
        } catch (e) {
            console.error(e);
            setSynthesizing(false);
        }
    };

    return (
        <div 
            ref={setNodeRef}
            className={clsx(
                "bg-white rounded-xl shadow-sm border-2 transition-all overflow-hidden",
                isOver ? "border-brand-teal ring-4 ring-brand-teal/10" : "border-white ring-1 ring-slate-200"
            )}
        >
            {/* Header */}
            <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                <div className="flex items-center gap-3">
                    <div className="bg-brand-teal/10 text-brand-teal w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm">
                        1
                    </div>
                    <h3 className="font-bold text-slate-800">{node.title}</h3>
                </div>
                {node.source_refs.length > 0 && (
                    <span className="text-xs text-slate-500 bg-white border border-slate-200 px-2 py-1 rounded-full">
                        {node.source_refs.length} sources loaded
                    </span>
                )}
            </div>

            {/* Content / Drop Zone */}
            <div className="p-6 min-h-[120px] flex flex-col items-center justify-center text-center relative">
                {preview ? (
                    <div className="text-left w-full prose prose-sm max-w-none">
                        <div className="whitespace-pre-wrap text-slate-700">{preview}</div>
                    </div>
                ) : (
                    <div className="text-slate-400 flex flex-col items-center w-full">
                         {items.length === 0 ? (
                             <>
                                <Plus className="mb-2 opacity-50" />
                                <span className="text-sm italic">Drag policies here</span>
                             </>
                         ) : (
                             <div className="w-full">
                                <div className="text-sm text-slate-600 mb-4">Ready to synthesize {items.length} slides.</div>
                                
                                {/* Visual list of dragged sources */}
                                <div className="flex flex-col gap-2 mb-4 max-w-full p-2 w-full">
                                    <SortableContext items={items} strategy={verticalListSortingStrategy}>
                                        {items.map((refId) => (
                                            <SortableSlideThumbnail key={refId} id={refId} url={thumbnails[refId]} />
                                        ))}
                                    </SortableContext>
                                </div>

                                <button 
                                    onClick={handleSynthesize}
                                    disabled={synthesizing}
                                    className="bg-brand-teal text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 mx-auto hover:bg-teal-700 disabled:opacity-50"
                                >
                                    {synthesizing ? (
                                        <>Synthesizing...</>
                                    ) : (
                                        <><Sparkles size={16} /> Generate Draft</>
                                    )}
                                </button>
                             </div>
                         )}
                    </div>
                )}
            </div>
        </div>
    );
};
