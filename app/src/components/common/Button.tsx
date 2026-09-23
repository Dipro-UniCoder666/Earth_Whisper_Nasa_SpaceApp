import { forwardRef } from 'react'
import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { cn } from '@/lib/utils'

type ButtonVariant = 'primary' | 'secondary' | 'ghost'
type ButtonSize = 'md' | 'lg'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  icon?: ReactNode
  iconPosition?: 'left' | 'right'
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    'bg-[var(--color-navy)] text-white hover:bg-[#052945] shadow-[0_10px_30px_-12px_rgba(7,59,102,0.55)]',
  secondary:
    'bg-white text-[var(--color-navy)] border border-[var(--color-sky)] hover:border-[var(--color-primary)] hover:bg-[var(--color-sky)]',
  ghost: 'bg-transparent text-[var(--color-navy)] hover:bg-[var(--color-sky)]',
}

const sizeClasses: Record<ButtonSize, string> = {
  md: 'px-5 py-2.5 text-[0.95rem]',
  lg: 'px-7 py-4 text-base',
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', icon, iconPosition = 'right', className, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center gap-2.5 rounded-full font-medium transition-all duration-300 ease-out',
          'focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[var(--color-primary)]',
          'disabled:opacity-50 disabled:pointer-events-none',
          variantClasses[variant],
          sizeClasses[size],
          className,
        )}
        {...props}
      >
        {icon && iconPosition === 'left' && <span className="shrink-0">{icon}</span>}
        <span>{children}</span>
        {icon && iconPosition === 'right' && (
          <span className="shrink-0 transition-transform duration-300 group-hover:translate-x-1">{icon}</span>
        )}
      </button>
    )
  },
)

Button.displayName = 'Button'
