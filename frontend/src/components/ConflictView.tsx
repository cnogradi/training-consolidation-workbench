import React from 'react';
import { AlertTriangle, CheckCircle } from 'lucide-react';

export const ConflictView: React.FC = () => {
    return (
        <div className="w-1/4 bg-white border-l border-slate-200 flex flex-col h-full">
            <div className="p-4 border-b border-slate-100 bg-red-50/50">
                <div className="flex items-center gap-2 text-red-600 mb-1">
                    <AlertTriangle size={16} />
                    <span className="font-bold text-sm">Conflicts Detected</span>
                </div>
                <h2 className="font-semibold text-slate-800">Unified Standard: Topic 1</h2>
                <p className="text-xs text-slate-500">Sources: 2 loaded</p>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                <div className="text-xs font-bold text-red-500 uppercase tracking-wider mb-2">
                    Policy Conflicts Detected
                </div>

                <div className="bg-white border border-red-100 rounded-lg shadow-sm p-3 relative">
                    <div className="absolute top-3 right-3 w-2 h-2 bg-blue-400 rounded-full"></div>
                    <div className="flex items-center gap-1 text-red-500 text-xs font-medium mb-1">
                        <AlertTriangle size={12} />
                        Conflict Found
                    </div>
                    <h3 className="font-semibold text-sm text-slate-800 mb-1">Tolerance Analysis</h3>
                    <p className="text-xs text-slate-500 leading-relaxed">
                        We strictly follow ASME Y14.5 standards for all geometric dimensioning. Stack-up analysis is required.
                    </p>
                </div>

                <div className="bg-white border border-red-100 rounded-lg shadow-sm p-3">
                     <div className="flex items-center gap-1 text-red-500 text-xs font-medium mb-1">
                        <AlertTriangle size={12} />
                        Conflict Found
                    </div>
                    <h3 className="font-semibold text-sm text-slate-800 mb-1">Design Change Process (ECR)</h3>
                    <p className="text-xs text-slate-500 leading-relaxed">
                       All Engineering Change Requests must be approved by a L3 Manager.
                    </p>
                </div>
                
                <div className="bg-green-50 border border-green-100 rounded-lg p-4 text-center mt-8">
                    <CheckCircle className="mx-auto text-green-500 mb-2" size={24} />
                    <p className="text-sm font-medium text-slate-700">Resolve conflicts to proceed</p>
                </div>
            </div>
        </div>
    );
};
