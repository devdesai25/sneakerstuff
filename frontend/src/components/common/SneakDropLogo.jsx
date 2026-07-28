import React from 'react';

/**
 * SneakDrop Logo - Geometric Athletic Streetwear Wordmark & Icon Mark
 * High-contrast Nike / Foot Locker visual style with Electric Red / Volt accent.
 */
export default function SneakDropLogo({ size = "md", showWordmark = true, className = "" }) {
  const heights = {
    sm: 24,
    md: 32,
    lg: 44,
    xl: 56
  };
  const iconSize = heights[size] || 32;

  return (
    <div className={`sneakdrop-logo-container ${className}`} style={{ display: 'inline-flex', alignItems: 'center', gap: '10px', textDecoration: 'none', userSelect: 'none' }}>
      {/* Dynamic Geometric Athletic Mark: Angular 'S' / Lightning Swoosh Hybrid */}
      <svg 
        width={iconSize} 
        height={iconSize} 
        viewBox="0 0 40 40" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
        style={{ flexShrink: 0, transform: 'skewX(-6deg)' }}
      >
        {/* Background angled shield / badge */}
        <rect width="40" height="40" rx="4" fill="#0A0A0A" />
        
        {/* Upper swoosh / lightning segment */}
        <path 
          d="M 28 8 L 12 16 L 22 18 L 10 28 L 22 28 L 30 18 L 18 16 Z" 
          fill="var(--accent-red, #FF2A00)" 
        />
        
        {/* Lower dynamic accent stroke */}
        <path 
          d="M 12 32 L 28 32 L 32 28 L 24 28 Z" 
          fill="#FFFFFF" 
        />
      </svg>

      {showWordmark && (
        <span 
          className="sneakdrop-wordmark"
          style={{
            fontFamily: 'var(--font-display, "Bebas Neue", "Outfit", sans-serif)',
            fontSize: size === 'sm' ? '20px' : size === 'lg' ? '32px' : size === 'xl' ? '40px' : '26px',
            fontWeight: 900,
            letterSpacing: '0.04em',
            lineHeight: 1,
            color: 'var(--text-primary, #FFFFFF)',
            textTransform: 'uppercase',
            display: 'inline-flex',
            alignItems: 'center'
          }}
        >
          SNEAK<span style={{ color: 'var(--accent-red, #FF2A00)', marginLeft: '1px' }}>DROP</span>
        </span>
      )}
    </div>
  );
}
