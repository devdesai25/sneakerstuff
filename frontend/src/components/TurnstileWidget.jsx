import React, { useEffect, useRef, useState } from 'react';

const TURNSTILE_SITE_KEY = import.meta.env.VITE_CLOUDFLARE_TURNSTILE_SITE_KEY || "3x0000000000000000000000000000000AA";

export default function TurnstileWidget({ onVerify, onError, resetKey }) {
  const containerRef = useRef(null);
  const widgetIdRef = useRef(null);
  const [scriptError, setScriptError] = useState(false);
  const [devVerified, setDevVerified] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setScriptError(false);
    setDevVerified(false);

    const renderWidget = () => {
      if (window.turnstile && containerRef.current && isMounted) {
        if (widgetIdRef.current !== null) {
          try {
            window.turnstile.remove(widgetIdRef.current);
          } catch (e) {
            // Ignore error if already removed
          }
          widgetIdRef.current = null;
        }

        try {
          const id = window.turnstile.render(containerRef.current, {
            sitekey: TURNSTILE_SITE_KEY,
            callback: (token) => {
              if (isMounted && onVerify) onVerify(token);
            },
            'error-callback': (err) => {
              console.warn("Cloudflare Turnstile error:", err);
              if (isMounted) {
                setScriptError(true);
                if (onError) onError(err);
              }
            },
            'expired-callback': () => {
              if (isMounted && onVerify) onVerify(null);
            },
            theme: 'dark',
          });
          widgetIdRef.current = id;
        } catch (err) {
          console.error("Turnstile render exception:", err);
          if (isMounted) setScriptError(true);
        }
      }
    };

    if (window.turnstile) {
      renderWidget();
    } else {
      const scriptId = 'cf-turnstile-script';
      let script = document.getElementById(scriptId);

      if (!script) {
        script = document.createElement('script');
        script.id = scriptId;
        script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
        script.async = true;
        script.defer = true;
        script.onerror = () => {
          if (isMounted) setScriptError(true);
        };
        document.head.appendChild(script);
      }

      let attempts = 0;
      const checkInterval = setInterval(() => {
        attempts++;
        if (window.turnstile) {
          clearInterval(checkInterval);
          renderWidget();
        } else if (attempts > 40) {
          clearInterval(checkInterval);
          if (isMounted) setScriptError(true);
        }
      }, 100);

      return () => {
        clearInterval(checkInterval);
      };
    }

    return () => {
      isMounted = false;
      if (window.turnstile && widgetIdRef.current !== null) {
        try {
          window.turnstile.remove(widgetIdRef.current);
        } catch (e) {}
      }
    };
  }, [resetKey]);

  const handleDevBypass = (e) => {
    const checked = e.target.checked;
    setDevVerified(checked);
    if (checked) {
      if (onVerify) onVerify("1x0000000000000000000000000000000AA");
    } else {
      if (onVerify) onVerify(null);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '12px 0' }}>
      <div ref={containerRef} />
      {scriptError && (
        <div style={{
          padding: '10px 14px',
          backgroundColor: 'rgba(255, 193, 7, 0.1)',
          border: '1px solid #ffc107',
          borderRadius: '6px',
          color: '#ffc107',
          fontSize: '12px',
          textAlign: 'center',
          maxWidth: '320px'
        }}>
          <p style={{ margin: '0 0 6px 0', fontWeight: 'bold' }}>Cloudflare Turnstile blocked or unavailable</p>
          <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input type="checkbox" checked={devVerified} onChange={handleDevBypass} />
            <span>Verify human for testing</span>
          </label>
        </div>
      )}
    </div>
  );
}
