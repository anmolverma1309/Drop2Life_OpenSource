import type { FeatureData } from './FeatureData';

interface FeatureNodeProps {
    feature: FeatureData;
    x: number;
    y: number;
    isHovered: boolean;
    isCore: boolean;
    onHover: (id: string | null) => void;
    absolute?: boolean;
}

export const FeatureNode = ({ feature, x, y, isHovered, isCore, onHover, absolute }: FeatureNodeProps) => {
    const isCategory = feature.parent === 'core' && !isCore;

    const posStyle = absolute
        ? { left: x, top: y, transform: 'translate(-50%, -50%)' }
        : { left: `calc(50% + ${x}px)`, top: `calc(50% + ${y}px)`, transform: 'translate(-50%, -50%)' };

    return (
        <div
            className={`absolute font-mono cursor-pointer shadow-lg transition-all duration-200 whitespace-nowrap
                ${isCore
                    ? 'px-8 py-4 rounded-full bg-slate-900/95 border-2 border-emerald-400 text-emerald-300 font-bold uppercase shadow-[0_0_30px_rgba(52,211,153,0.35)] text-lg tracking-[0.2em] z-20'
                    : isCategory
                        ? 'px-6 py-3 rounded-lg bg-slate-800/90 border border-emerald-400/50 text-emerald-200 text-base uppercase tracking-[0.15em] z-15'
                        : `px-5 py-2.5 rounded-md border text-base text-slate-100 tracking-wide z-10 ${isHovered ? 'bg-teal-900/70 border-teal-300 shadow-[0_0_12px_rgba(45,212,191,0.35)]' : 'bg-slate-800/80 border-slate-600 hover:border-emerald-300/70'}`
                }
            `}
            style={posStyle}
            onMouseEnter={() => onHover(feature.id)}
            onMouseLeave={() => onHover(null)}
        >
            {feature.title}
        </div>
    );
};
