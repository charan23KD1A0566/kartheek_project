import { useEffect, useRef } from 'react'

export default function CursorFX() {
  const dotRef = useRef(null)
  const glowRef = useRef(null)
  const ringRef = useRef(null)

  const mouse = useRef({
    x: window.innerWidth / 2,
    y: window.innerHeight / 2,
  })

  const position = useRef({
    x: window.innerWidth / 2,
    y: window.innerHeight / 2,
  })

  const previous = useRef({
    x: window.innerWidth / 2,
    y: window.innerHeight / 2,
  })

  const rafRef = useRef(null)

  useEffect(() => {
    // Don't run cursor effects on touch/mobile devices
    const isTouchDevice =
      window.matchMedia('(pointer: coarse)').matches ||
      'ontouchstart' in window

    if (isTouchDevice) return

    const handleMouseMove = (event) => {
      mouse.current.x = event.clientX
      mouse.current.y = event.clientY

      // Detect interactive elements
      const target = event.target.closest(
        'button, a, input, textarea, select, [role="button"], .btn, .card, .panel'
      )

      if (target) {
        document.body.classList.add('cursor-interactive')
      } else {
        document.body.classList.remove('cursor-interactive')
      }
    }

    const handleMouseDown = () => {
      document.body.classList.add('cursor-clicking')
    }

    const handleMouseUp = () => {
      document.body.classList.remove('cursor-clicking')
    }

    const handleMouseLeave = () => {
      document.body.classList.add('cursor-hidden')
    }

    const handleMouseEnter = () => {
      document.body.classList.remove('cursor-hidden')
    }

    window.addEventListener('mousemove', handleMouseMove, {
      passive: true,
    })

    window.addEventListener('mousedown', handleMouseDown)

    window.addEventListener('mouseup', handleMouseUp)

    document.documentElement.addEventListener(
      'mouseleave',
      handleMouseLeave
    )

    document.documentElement.addEventListener(
      'mouseenter',
      handleMouseEnter
    )

    /*
      Smooth animation loop.

      The cursor itself follows quickly.
      The glow and ring follow more slowly,
      creating a subtle premium trailing effect.
    */
    const animate = () => {
      const targetX = mouse.current.x
      const targetY = mouse.current.y

      // Main dot — very responsive
      position.current.x +=
        (targetX - position.current.x) * 0.42

      position.current.y +=
        (targetY - position.current.y) * 0.42

      // Calculate movement speed
      const dx =
        targetX - previous.current.x

      const dy =
        targetY - previous.current.y

      const speed = Math.min(
        Math.sqrt(dx * dx + dy * dy),
        35
      )

      previous.current.x = targetX
      previous.current.y = targetY

      if (dotRef.current) {
        dotRef.current.style.transform =
          `translate3d(${position.current.x}px, ${position.current.y}px, 0)`
      }

      // Glow follows slowly
      if (glowRef.current) {
        const glowX =
          position.current.x * 0.75 +
          targetX * 0.25

        const glowY =
          position.current.y * 0.75 +
          targetY * 0.25

        glowRef.current.style.transform =
          `translate3d(${glowX}px, ${glowY}px, 0)`
      }

      // Outer ring has slightly more delay
      if (ringRef.current) {
        const ringX =
          position.current.x * 0.55 +
          targetX * 0.45

        const ringY =
          position.current.y * 0.55 +
          targetY * 0.45

        ringRef.current.style.transform =
          `translate3d(${ringX}px, ${ringY}px, 0)`

        // Very subtle movement-based scale
        const scale =
          1 + speed * 0.002

        ringRef.current.style.setProperty(
          '--cursor-scale',
          scale
        )
      }

      rafRef.current =
        requestAnimationFrame(animate)
    }

    rafRef.current =
      requestAnimationFrame(animate)

    return () => {
      window.removeEventListener(
        'mousemove',
        handleMouseMove
      )

      window.removeEventListener(
        'mousedown',
        handleMouseDown
      )

      window.removeEventListener(
        'mouseup',
        handleMouseUp
      )

      document.documentElement.removeEventListener(
        'mouseleave',
        handleMouseLeave
      )

      document.documentElement.removeEventListener(
        'mouseenter',
        handleMouseEnter
      )

      document.body.classList.remove(
        'cursor-interactive',
        'cursor-clicking',
        'cursor-hidden'
      )

      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current)
      }
    }
  }, [])

  return (
    <>
      {/* Small ambient glow */}
      <div
        ref={glowRef}
        className="cursor-fx-glow"
        aria-hidden="true"
      />

      {/* Delayed outer ring */}
      <div
        ref={ringRef}
        className="cursor-fx-ring"
        aria-hidden="true"
      />

      {/* Main cursor point */}
      <div
        ref={dotRef}
        className="cursor-fx-dot"
        aria-hidden="true"
      />
    </>
  )
}