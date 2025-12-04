import React, { useEffect, useRef, useState } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Link from '@tiptap/extension-link';
import { Bold, Italic, List, ListOrdered, Heading2, Link as LinkIcon, Code } from 'lucide-react';
import clsx from 'clsx';
import { marked } from 'marked';
import TurndownService from 'turndown';

interface MarkdownEditorProps {
    content: string;
    onSave: (markdown: string) => void;
}

// Initialize turndown for HTML to Markdown conversion
const turndownService = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced',
});

export const MarkdownEditor: React.FC<MarkdownEditorProps> = ({ content, onSave }) => {
    const lastSavedContent = useRef(content);
    const [viewMode, setViewMode] = useState<'wysiwyg' | 'markdown'>('wysiwyg');
    const [markdownText, setMarkdownText] = useState(content);

    const editor = useEditor({
        extensions: [
            StarterKit.configure({
                heading: {
                    levels: [1, 2, 3],
                },
            }),
            Placeholder.configure({
                placeholder: 'Start editing the synthesized content...',
            }),
            Link.configure({
                openOnClick: false,
            }),
        ],
        // Convert markdown to HTML for initial content
        content: marked.parse(content || '') as string,
        editorProps: {
            attributes: {
                class: 'prose prose-sm max-w-none focus:outline-none min-h-[200px] p-3',
            },
        },
        onUpdate: ({ editor }) => {
            // Convert HTML back to markdown
            const html = editor.getHTML();
            const markdown = turndownService.turndown(html);

            // Only save if content actually changed
            if (markdown !== lastSavedContent.current) {
                lastSavedContent.current = markdown;
                setMarkdownText(markdown);
                onSave(markdown);
            }
        },
    });

    // Update editor content when prop changes externally
    useEffect(() => {
        if (editor && content !== lastSavedContent.current) {
            const html = marked.parse(content || '') as string;
            editor.commands.setContent(html);
            lastSavedContent.current = content;
            setMarkdownText(content);
        }
    }, [content, editor]);

    if (!editor) {
        return <div className="p-4 text-slate-400 text-sm">Loading editor...</div>;
    }

    return (
        <div className="border border-slate-200 rounded-lg bg-white overflow-hidden">
            {/* Toolbar */}
            <div className="flex items-center justify-between gap-1 p-2 bg-slate-50 border-b border-slate-200 flex-wrap">
                <div className="flex items-center gap-1">
                    {viewMode === 'wysiwyg' && (
                        <>
                            <button
                                onClick={() => editor.chain().focus().toggleBold().run()}
                                className={clsx(
                                    'p-1.5 rounded hover:bg-slate-200 transition-colors',
                                    editor.isActive('bold') ? 'bg-slate-200 text-brand-teal' : 'text-slate-600'
                                )}
                                title="Bold (Ctrl+B)"
                            >
                                <Bold size={14} />
                            </button>
                            <button
                                onClick={() => editor.chain().focus().toggleItalic().run()}
                                className={clsx(
                                    'p-1.5 rounded hover:bg-slate-200 transition-colors',
                                    editor.isActive('italic') ? 'bg-slate-200 text-brand-teal' : 'text-slate-600'
                                )}
                                title="Italic (Ctrl+I)"
                            >
                                <Italic size={14} />
                            </button>
                            <div className="w-px h-4 bg-slate-300 mx-1" />
                            <button
                                onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
                                className={clsx(
                                    'p-1.5 rounded hover:bg-slate-200 transition-colors',
                                    editor.isActive('heading', { level: 2 }) ? 'bg-slate-200 text-brand-teal' : 'text-slate-600'
                                )}
                                title="Heading 2"
                            >
                                <Heading2 size={14} />
                            </button>
                            <div className="w-px h-4 bg-slate-300 mx-1" />
                            <button
                                onClick={() => editor.chain().focus().toggleBulletList().run()}
                                className={clsx(
                                    'p-1.5 rounded hover:bg-slate-200 transition-colors',
                                    editor.isActive('bulletList') ? 'bg-slate-200 text-brand-teal' : 'text-slate-600'
                                )}
                                title="Bullet List"
                            >
                                <List size={14} />
                            </button>
                            <button
                                onClick={() => editor.chain().focus().toggleOrderedList().run()}
                                className={clsx(
                                    'p-1.5 rounded hover:bg-slate-200 transition-colors',
                                    editor.isActive('orderedList') ? 'bg-slate-200 text-brand-teal' : 'text-slate-600'
                                )}
                                title="Ordered List"
                            >
                                <ListOrdered size={14} />
                            </button>
                            <div className="w-px h-4 bg-slate-300 mx-1" />
                            <button
                                onClick={() => {
                                    const url = window.prompt('Enter URL:');
                                    if (url) {
                                        editor.chain().focus().setLink({ href: url }).run();
                                    }
                                }}
                                className={clsx(
                                    'p-1.5 rounded hover:bg-slate-200 transition-colors',
                                    editor.isActive('link') ? 'bg-slate-200 text-brand-teal' : 'text-slate-600'
                                )}
                                title="Add Link"
                            >
                                <LinkIcon size={14} />
                            </button>
                        </>
                    )}
                </div>

                {/* Toggle between WYSIWYG and Markdown */}
                <button
                    onClick={() => setViewMode(viewMode === 'wysiwyg' ? 'markdown' : 'wysiwyg')}
                    className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-slate-600 hover:text-brand-teal hover:bg-slate-100 rounded transition-colors"
                    title={viewMode === 'wysiwyg' ? 'View Raw Markdown' : 'View Rich Editor'}
                >
                    <Code size={12} />
                    {viewMode === 'wysiwyg' ? 'View Markdown' : 'View Editor'}
                </button>
            </div>

            {/* Editor Content */}
            {viewMode === 'wysiwyg' ? (
                <EditorContent editor={editor} className="bg-white" />
            ) : (
                <textarea
                    value={markdownText}
                    onChange={(e) => {
                        const newMarkdown = e.target.value;
                        setMarkdownText(newMarkdown);

                        // Update TipTap editor with new markdown
                        const html = marked.parse(newMarkdown || '') as string;
                        editor.commands.setContent(html);

                        // Save
                        lastSavedContent.current = newMarkdown;
                        onSave(newMarkdown);
                    }}
                    className="w-full min-h-[200px] p-3 font-mono text-sm text-slate-700 bg-white focus:outline-none resize-none"
                    placeholder="Enter markdown here..."
                />
            )}
        </div>
    );
};
