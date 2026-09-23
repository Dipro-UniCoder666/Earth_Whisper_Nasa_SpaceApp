import { useNavigate } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { Button } from '@/components/common/Button'
import { ROUTES } from '@/lib/constants'

/** The one and only call to action on the landing page. */
export function HeroCTA() {
  const navigate = useNavigate()

  return (
    <Button
      size="lg"
      icon={<ArrowRight size={20} />}
      onClick={() => navigate(ROUTES.investigate)}
      className="group"
    >
      Begin the Investigation
    </Button>
  )
}
