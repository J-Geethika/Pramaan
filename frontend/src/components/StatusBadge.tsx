type Props = {
  value: 'low' | 'medium' | 'high' | 'pending' | 'under_review' | 'resolved' | 'dismissed'
}

const styles: Record<Props['value'], string> = {
  low: 'bg-sky-100 text-sky-800',
  medium: 'bg-amber-100 text-amber-800',
  high: 'bg-rose-100 text-rose-800',
  pending: 'bg-slate-100 text-slate-700',
  under_review: 'bg-indigo-100 text-indigo-700',
  resolved: 'bg-emerald-100 text-emerald-700',
  dismissed: 'bg-zinc-100 text-zinc-700',
}

export default function StatusBadge({ value }: Props) {
  return (
    <span className={`rounded-full px-2 py-1 text-xs font-semibold uppercase tracking-wide ${styles[value]}`}>
      {value.replace('_', ' ')}
    </span>
  )
}
