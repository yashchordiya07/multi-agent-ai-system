function Skel({ w = "w-full", h = "h-3" }) {
  return <div className={`skeleton ${h} ${w}`} />;
}

function CardSkel({ borderColor }) {
  return (
    <div className={`card border ${borderColor} space-y-3`}>
      <div className="flex items-center gap-3">
        <div className="skeleton w-8 h-8 rounded-xl" />
        <Skel w="w-32" h="h-4" />
        <div className="ml-auto skeleton w-20 h-5 rounded-full" />
      </div>
      <Skel /><Skel w="w-5/6" /><Skel w="w-4/6" />
    </div>
  );
}

export default function LoadingSkeleton() {
  return (
    <div className="space-y-4 animate-fade-in">
      <div className="card border border-surface-border flex items-center gap-4 py-4">
        <div className="w-7 h-7 rounded-full border-2 border-violet-500 border-t-transparent animate-spin flex-shrink-0" />
        <div className="space-y-2 flex-1">
          <Skel w="w-48" h="h-3.5" />
          <Skel w="w-36" h="h-3" />
        </div>
      </div>
      <CardSkel borderColor="border-blue-500/20"   />
      <CardSkel borderColor="border-violet-500/20" />
      <CardSkel borderColor="border-amber-500/20"  />
    </div>
  );
}
