import type { HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  padding?: 'sm' | 'md' | 'lg'
}

const paddingClasses = {
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
}

/**
 * A quiet, mostly-solid surface with a whisper of translucency and a soft
 * shadow — deliberately restrained rather than a heavy frosted-glass panel.
 */
export function GlassCard({ padding = 'md', className, children, ...props }: GlassCardProps) {
  return (
    <div
      className={cn(
        'rounded-2xl border border-[var(--color-sky)] bg-white/90 backdrop-blur-sm',
        'shadow-[0_20px_50px_-30px_rgba(7,59,102,0.35)]',
        paddingClasses[padding],
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}
