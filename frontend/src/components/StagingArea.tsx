import React, { useEffect, useState } from 'react';
import { ArrowRight, Layers, Zap } from 'lucide-react';
import { api } from '../api';
import type { CourseSection } from '../api';
import { useSelectionStore } from '../stores/selectionStore';
import { useAppStore } from '../store';
import clsx from 'clsx';

interface StagingGroup {
    buName: string;
    courses: {
        id: string;
        title: string;
        sections: CourseSection[];
    }[];
}

export const StagingArea: React.FC = () => {
    const { selectedSourceIds } = useSelectionStore();
    const { setStagingMode, setProjectId } = useAppStore();
    const [groups, setGroups] = useState<StagingGroup[]>([]);
    const [loading, setLoading] = useState(true);
    const [strategy, setStrategy] = useState<'union' | 'intersection'>('union');
    const [sharedConcepts, setSharedConcepts] = useState<Set<string>>(new Set());

    // Fetch sections for all selected courses
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                // First, get the tree to know which BU each course belongs to
                const tree = await api.getSourceTree();

                // Fetch sections for each selected course
                const coursesData: { id: string; title: string; bu: string; sections: CourseSection[] }[] = [];

                for (const courseId of Array.from(selectedSourceIds)) {
                    // Find the course in the tree to get its BU
                    let courseBU = 'Unknown';
                    let courseTitle = '';

                    for (const bu of tree) {
                        const course = bu.children?.find(c => c.id === courseId);
                        if (course) {
                            courseBU = bu.name;
                            courseTitle = course.name;
                            break;
                        }
                    }

                    // Fetch sections
                    const sections = await api.getCourseSections(courseId);
                    coursesData.push({
                        id: courseId,
                        title: courseTitle,
                        bu: courseBU,
                        sections
                    });
                }

                // Group by BU
                const grouped = coursesData.reduce((acc, course) => {
                    const existing = acc.find(g => g.buName === course.bu);
                    if (existing) {
                        existing.courses.push({
                            id: course.id,
                            title: course.title,
                            sections: course.sections
                        });
                    } else {
                        acc.push({
                            buName: course.bu,
                            courses: [{
                                id: course.id,
                                title: course.title,
                                sections: course.sections
                            }]
                        });
                    }
                    return acc;
                }, [] as StagingGroup[]);

                setGroups(grouped);

                // Calculate shared concepts (present in at least 2 BUs)
                if (grouped.length >= 2) {
                    const conceptsByBU = grouped.map(g => {
                        const concepts = new Set<string>();
                        g.courses.forEach(c => {
                            c.sections.forEach(s => {
                                s.concepts?.forEach(concept => concepts.add(concept));
                            });
                        });
                        return concepts;
                    });

                    const shared = new Set<string>();
                    conceptsByBU.forEach((buConcepts, i) => {
                        buConcepts.forEach(concept => {
                            // Check if this concept appears in at least one other BU
                            const appearsInOtherBU = conceptsByBU.some((otherBUConcepts, j) =>
                                i !== j && otherBUConcepts.has(concept)
                            );
                            if (appearsInOtherBU) {
                                shared.add(concept);
                            }
                        });
                    });

                    setSharedConcepts(shared);
                }

            } catch (error) {
                console.error('Failed to fetch staging data:', error);
            } finally {
                setLoading(false);
            }
        };

        if (selectedSourceIds.size > 0) {
            fetchData();
        }
    }, [selectedSourceIds]);

    const handleGenerate = async () => {
        try {
            const result = await api.generateProjectSkeleton({
                title: `Consolidated Curriculum`,
                domain: null,
                selected_source_ids: Array.from(selectedSourceIds)
            });

            // Switch back to consolidation view and load the new project
            setStagingMode(false);
            setProjectId(result.project_id);
        } catch (error) {
            console.error('Failed to generate outline:', error);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="animate-spin text-brand-teal">
                    <Layers size={48} />
                </div>
            </div>
        );
    }

    const gridClass = groups.length === 1 ? 'grid-cols-1' : groups.length === 2 ? 'grid-cols-2' : 'grid-cols-3';

    return (
        <div className="flex flex-col h-full bg-slate-50">
            {/* Header with Generate Button */}
            <div className="bg-white border-b border-slate-200 p-4 space-y-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Layers className="text-blue-600" size={24} />
                        <div>
                            <h2 className="font-bold text-slate-800">Staging & Comparison</h2>
                            <p className="text-xs text-slate-500">Review selected courses before generating outline</p>
                        </div>
                    </div>
                    <button
                        onClick={handleGenerate}
                        className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                    >
                        <Zap size={16} />
                        Generate Outline
                    </button>
                </div>

                {/* Strategy Toggle */}
                <div className="flex items-center gap-4">
                    <span className="text-sm font-medium text-slate-700">Merge Strategy:</span>
                    <div className="flex gap-3">
                        <button
                            onClick={() => setStrategy('union')}
                            className={clsx(
                                'px-4 py-2 rounded-md text-sm font-medium transition-all border-2',
                                strategy === 'union'
                                    ? 'bg-blue-600 text-white border-blue-600'
                                    : 'bg-white text-slate-700 border-slate-300 hover:border-blue-400 hover:bg-slate-50'
                            )}
                        >
                            Union (All Concepts)
                        </button>
                        <button
                            onClick={() => setStrategy('intersection')}
                            className={clsx(
                                'px-4 py-2 rounded-md text-sm font-medium transition-all border-2',
                                strategy === 'intersection'
                                    ? 'bg-blue-600 text-white border-blue-600'
                                    : 'bg-white text-slate-700 border-slate-300 hover:border-blue-400 hover:bg-slate-50'
                            )}
                        >
                            Intersection (Shared Only)
                        </button>
                    </div>
                    {strategy === 'intersection' && sharedConcepts.size > 0 && (
                        <span className="text-xs text-slate-500">
                            {sharedConcepts.size} shared concepts
                        </span>
                    )}
                </div>
            </div>

            {/* Main Grid */}
            <div className={clsx('grid h-full divide-x divide-gray-200 overflow-hidden', gridClass)}>
                {groups.map((group, idx) => (
                    <div key={idx} className="flex flex-col overflow-hidden">
                        {/* Column Header */}
                        <div className="bg-slate-100 border-b border-slate-200 p-3 flex-shrink-0">
                            <h3 className="font-bold text-sm text-slate-700">{group.buName}</h3>
                            <p className="text-xs text-slate-500">
                                {group.courses.length} course{group.courses.length !== 1 ? 's' : ''}
                            </p>
                        </div>

                        {/* Course Cards */}
                        <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-4">
                            {group.courses.map(course => (
                                <div key={course.id} className="border border-gray-300 rounded bg-white shadow-sm">
                                    {/* Course Title */}
                                    <div className="bg-gray-100 p-3 border-b border-gray-200">
                                        <h4 className="font-bold text-sm text-slate-800">{course.title}</h4>
                                        <p className="text-xs text-slate-500 mt-1">
                                            {course.sections.length} section{course.sections.length !== 1 ? 's' : ''}
                                        </p>
                                    </div>

                                    {/* Sections List */}
                                    <div className="p-3 space-y-2">
                                        {course.sections.length === 0 ? (
                                            <p className="text-xs text-slate-400 italic">No sections found</p>
                                        ) : (
                                            course.sections.map(section => (
                                                <div key={section.id} className="pb-2 border-b border-slate-100 last:border-0">
                                                    <div className="flex items-start gap-2">
                                                        <ArrowRight size={12} className="text-slate-400 mt-0.5 flex-shrink-0" />
                                                        <div className="flex-1 min-w-0">
                                                            <p className="text-xs font-medium text-slate-700">
                                                                {section.title}
                                                            </p>
                                                            {/* Concepts */}
                                                            {section.concepts && section.concepts.length > 0 && (
                                                                <div className="flex flex-wrap gap-1 mt-1">
                                                                    {section.concepts.map((concept, i) => {
                                                                        const isShared = sharedConcepts.has(concept);
                                                                        const isDimmed = strategy === 'intersection' && !isShared;

                                                                        return (
                                                                            <span
                                                                                key={i}
                                                                                className={clsx(
                                                                                    'text-[10px] px-1.5 py-0.5 rounded border',
                                                                                    isDimmed
                                                                                        ? 'bg-slate-50 text-slate-300 border-slate-200'
                                                                                        : isShared && strategy === 'intersection'
                                                                                            ? 'bg-blue-100 text-blue-700 border-blue-300 font-medium'
                                                                                            : 'bg-slate-100 text-slate-600 border-slate-200'
                                                                                )}
                                                                            >
                                                                                {concept}
                                                                            </span>
                                                                        );
                                                                    })}
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
