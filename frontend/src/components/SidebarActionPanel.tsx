import { useSelectionStore } from '../stores/selectionStore';
import { useAppStore } from '../store';

export function SidebarActionPanel() {
    const { selectedSourceIds, clearSelection } = useSelectionStore();

    const count = selectedSourceIds.size;

    // Only show when items are selected
    if (count === 0) return null;

    const handleReview = () => {
        useAppStore.setState({ stagingMode: true });
    };

    return (
        <div className="absolute bottom-4 left-4 right-4 w-auto max-w-xs
                    bg-white border-2 border-blue-600 rounded-lg shadow-2xl p-4 z-[100]">
            <div className="flex flex-col gap-3">
                {/* Selection count */}
                <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">
                        {count} item{count !== 1 ? 's' : ''} selected
                    </span>
                    <button
                        onClick={() => clearSelection()}
                        className="text-xs text-gray-500 hover:text-gray-700"
                    >
                        Clear
                    </button>
                </div>

                {/* Review button */}
                <button
                    onClick={handleReview}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700
                     flex items-center justify-center gap-2 font-medium transition-colors"
                >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                        />
                    </svg>
                    Review Selected
                </button>
            </div>
        </div>
    );
}
