import { ShieldCheck, ShieldAlert, ShieldX } from "lucide-react";

const MAP = {
  high:   { cls: "badge-green",  Icon: ShieldCheck, label: "High confidence"   },
  medium: { cls: "badge-amber",  Icon: ShieldAlert, label: "Medium confidence" },
  low:    { cls: "badge-red",    Icon: ShieldX,     label: "Low confidence"    },
};

export default function ConfidenceBadge({ level }) {
  const { cls, Icon, label } = MAP[level?.toLowerCase()] ?? MAP.medium;
  return (
    <span className={`badge ${cls}`}>
      <Icon size={11} />
      {label}
    </span>
  );
}
