import { X } from 'lucide-react'
import { IconButton } from '@/components/common/IconButton'
import { cn } from '@/lib/utils'

interface MobileMenuLink {
  label: string
  href: string
  external?: boolean
}

interface MobileMenuProps {
  open: boolean
  onClose: () => void
  links: readonly MobileMenuLink[]
  children?: React.ReactNode
}

export function MobileMenu({ open, onClose, links, children }: MobileMenuProps) {
  return (
    <div
      className={cn(
        'fixed inset-0 z-50 bg-white transition-opacity duration-300 md:hidden',
        open ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0',
      )}
      role="dialog"
      aria-modal="true"
      aria-label="Navigation menu"
    >
      <div className="flex items-center justify-end px-6 py-5">
        <IconButton icon={<X size={22} />} label="Close menu" onClick={onClose} />
      </div>
      <nav className="flex flex-col gap-1 px-6 pt-4">
        {links.map((link) => (
          <a
            key={link.label}
            href={link.href}
            target={link.external ? '_blank' : undefined}
            rel={link.external ? 'noreferrer' : undefined}
            onClick={onClose}
            className="border-b border-[var(--color-sky)] py-4 text-lg font-medium text-[var(--color-navy)]"
          >
            {link.label}
          </a>
        ))}
      </nav>
      {children && <div className="mt-6 px-6">{children}</div>}
    </div>
  )
}
