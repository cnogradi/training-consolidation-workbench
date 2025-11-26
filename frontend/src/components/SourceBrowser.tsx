import React, { useEffect, useState } from 'react';
import { Search, Folder, ChevronDown, FileText, Image } from 'lucide-react';
import { api } from '../api';
import type { CourseNode, SourceSlide } from '../api';
import { useDraggable } from '@dnd-kit/core';

interface SourceBrowserProps {
    discipline: string;
}

export const SourceBrowser: React.FC<SourceBrowserProps> = ({ discipline }) => {
    const [tree, setTree] = useState<CourseNode[]>([]);
    // const [expanded, setExpanded] = useState<Set<string>>(new Set());
    const [selectedCourse, setSelectedCourse] = useState<string | null>(null);
    const [slides, setSlides] = useState<SourceSlide[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        api.getSourceTree(discipline).then(setTree);
        // Reset selection when discipline changes
        setSelectedCourse(null);
        setSlides([]);
        // setExpanded(new Set()); // Reset expanded on discipline change
    }, [discipline]);

    // const toggleExpand = (id: string) => {
    //     const newExpanded = new Set(expanded);
    //     if (newExpanded.has(id)) newExpanded.delete(id);
    //     else newExpanded.add(id);
    //     setExpanded(newExpanded);
    // };

    const selectCourse = async (courseId: string) => {
        setSelectedCourse(courseId);
        setLoading(true);
        try {
            const slideRefs = await api.getCourseSlides(courseId);
            // Fetch full details for previews (or maybe optimize to only fetch needed ones?)
            // For now, just fetching the list. The API returns text but not S3 URL in the list endpoint?
            // Ah, getCourseSlides returns {id, number, text}. We need S3 URL.
            // The list endpoint didn't return S3 URL in my backend implementation.
            // I should check backend or fetch individual details.
            // Fetching individual details for all slides might be slow if many.
            // Let's fetch details for the first few or just construct the URL if possible?
            // The backend `get_slide_details` does construct it.
            // Ideally backend `getCourseSlides` should return S3 URLs.
            // For now, I will fetch details for each slide in parallel (limit 10?).
            // Or better, I'll just display text preview and fetch image on mount of the card.
            
            // Let's assume I can get details one by one.
            // Or I can update backend. But I can't right now easily without switching context.
            // I'll fetch details for all slides.
            const details = await Promise.all(slideRefs.map(s => api.getSlideDetails(s.id)));
            setSlides(details);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-1/4 bg-white border-r border-slate-200 flex flex-col h-full">
            {/* Header */}
            <div className="p-4 border-b border-slate-100">
                <div className="flex items-center gap-2 mb-3">
                    <Folder className="text-brand-teal" size={18} />
                    <h2 className="font-semibold text-slate-800">Legacy Content</h2>
                </div>
                <div className="relative">
                    <Search className="absolute left-3 top-2.5 text-slate-400" size={14} />
                    <input 
                        type="text" 
                        placeholder="Search concepts..." 
                        className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-md text-sm focus:outline-none focus:border-brand-teal"
                    />
                </div>
            </div>

            {/* Tree & Slides */}
            <div className="flex-1 overflow-y-auto p-2">
                {/* Business Units */}
                {tree.map(bu => (
                    <div key={bu.name}>
                        <div className="flex items-center gap-2 p-2 hover:bg-slate-50 rounded cursor-pointer font-medium text-slate-700 text-sm">
                            <ChevronDown size={14} />
                            {bu.name}
                        </div>
                        <div className="pl-4">
                            {bu.children?.map(course => (
                                <div key={course.id}>
                                    <div 
                                        className={`flex items-center gap-2 p-2 rounded cursor-pointer text-sm ${selectedCourse === course.id ? 'bg-brand-teal/10 text-brand-teal font-medium' : 'text-slate-600 hover:bg-slate-50'}`}
                                        onClick={() => selectCourse(course.id)}
                                    >
                                        <FileText size={14} />
                                        <span className="truncate">{course.name}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}

                {/* Divider */}
                {selectedCourse && <div className="my-4 border-t border-slate-100" />}

                {/* Slide List */}
                <div className="space-y-3 px-2 pb-10">
                    {loading ? (
                        <div className="text-center text-xs text-slate-400 py-4">Loading slides...</div>
                    ) : slides.map(slide => (
                        <SlideCard key={slide.id} slide={slide} />
                    ))}
                </div>
            </div>
        </div>
    );
};

const SlideCard: React.FC<{ slide: SourceSlide }> = ({ slide }) => {
    const { attributes, listeners, setNodeRef, transform } = useDraggable({
        id: slide.id,
        data: { slide }
    });
    
    const style = transform ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
        zIndex: 1000,
        opacity: 0.8
    } : undefined;

    return (
        <div 
            ref={setNodeRef} 
            {...listeners} 
            {...attributes} 
            style={style}
            className="bg-white border border-slate-200 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-grab active:cursor-grabbing overflow-hidden group"
        >
            <div className="p-2 bg-slate-50 border-b border-slate-100 flex justify-between items-center">
                <span className="text-xs font-medium text-slate-600 truncate max-w-[150px]">
                    {slide.concepts[0]?.name || 'General Slide'}
                </span>
                <span className="text-[10px] bg-slate-200 text-slate-600 px-1.5 py-0.5 rounded">PPTX</span>
            </div>
            <div className="h-32 bg-slate-100 flex items-center justify-center relative overflow-hidden">
                {slide.s3_url ? (
                    <img src={slide.s3_url} alt="Slide" className="w-full h-full object-cover" />
                ) : (
                    <Image className="text-slate-300" />
                )}
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors" />
            </div>
            <div className="p-2">
                <div className="flex flex-wrap gap-1">
                    {slide.concepts.slice(0, 3).map((c, i) => (
                        <span key={i} className="text-[10px] border border-slate-200 px-1.5 py-0.5 rounded text-slate-500">
                            {c.name}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
};
