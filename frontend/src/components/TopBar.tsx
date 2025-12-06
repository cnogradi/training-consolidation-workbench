import React from 'react';
import { Settings, Code, Activity, Globe, Cpu } from 'lucide-react';
import clsx from 'clsx';
import { LoginButton } from './LoginButton';
import { LogoutButton } from './LogoutButton';
import { useAuth } from 'react-oidc-context';

interface TopBarProps {
    discipline: string;
    setDiscipline: (d: string) => void;
}

export const TopBar: React.FC<TopBarProps> = ({ discipline, setDiscipline }) => {
    const auth = useAuth();
    const userDisplay = auth.user?.profile.preferred_username || auth.user?.profile.email || "Guest";

    const disciplines = [
        { id: 'Mechanical', label: 'ME', icon: Settings },
        { id: 'Electrical', label: 'EE', icon: Activity }, // Using Activity for waves/signals
        { id: 'Software', label: 'SWE', icon: Code },
        { id: 'Systems', label: 'SysE', icon: Globe }, // Globe for big picture? Or Cpu?
    ];

    return (
        <div className="h-14 bg-brand-dark text-white flex items-center justify-between px-4 shadow-md">
            <div className="flex items-center gap-3">
                <div className="bg-brand-teal p-1.5 rounded-lg">
                    <Cpu size={20} className="text-white" />
                </div>
                <div>
                    <h1 className="font-bold text-sm leading-tight">Training Consolidation Workbench</h1>
                    <p className="text-xs text-slate-400">Project: Global Standardization • User: {userDisplay}</p>
                </div>
            </div>

            <div className="flex bg-slate-800 rounded-lg p-1">
                <span className="px-3 py-1 text-xs text-slate-400 font-semibold self-center">DISCIPLINE:</span>
                {disciplines.map(d => (
                    <button
                        key={d.id}
                        onClick={() => setDiscipline(d.id)}
                        className={clsx(
                            "flex items-center gap-2 px-3 py-1 rounded-md text-sm transition-all",
                            discipline === d.id
                                ? "bg-brand-teal text-white shadow-sm font-medium"
                                : "text-slate-400 hover:text-slate-200"
                        )}
                    >
                        <d.icon size={14} />
                        {d.label}
                    </button>
                ))}
            </div>

            <div className="flex items-center gap-4 text-slate-400">
                {auth.user && (
                    <span className="text-xs text-slate-500 font-mono hidden xl:block">
                        ID: {auth.user.profile.sub?.substring(0, 8)}...
                    </span>
                )}
                <LoginButton />
                <LogoutButton />
                <Settings size={18} className="cursor-pointer hover:text-white" />
            </div>
        </div>
    );
};
