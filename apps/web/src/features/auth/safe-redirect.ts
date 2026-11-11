const UNSAFE_CHARACTERS = /[\u0000-\u001f\u007f\\]/;

/** Return a local route only; URL parsing can otherwise remove controls or normalize slashes. */
export function safeRedirectPath(value: string | null, origin: string): string | null {
  if (!value) return null;
  try {
    const base = new URL(origin);
    if (base.protocol !== "http:" && base.protocol !== "https:") return null;
    let decoded = value;
    // Inspect encoded forms too: useSearchParams has already decoded the outer query once.
    for (let depth = 0; depth < 8; depth += 1) {
      if (!decoded.startsWith("/") || decoded.startsWith("//") || UNSAFE_CHARACTERS.test(decoded)) return null;
      const parsed = new URL(decoded, base.origin);
      if (parsed.origin !== base.origin || parsed.pathname.startsWith("//")) return null;
      // Inspect encoded bytes even when another escape is malformed; it must not hide a control.
      // Keep the original URL for routing so UTF-8 and literal percent queries stay intact.
      const next = decoded.replace(/%([0-9a-f]{2})/gi, (_match, hex: string) => String.fromCharCode(Number.parseInt(hex, 16)));
      if (next === decoded) break;
      if (depth === 7) return null;
      decoded = next;
    }
    const destination = new URL(value, base.origin);
    // Never hand router.push a protocol-relative result after path normalization.
    if (destination.origin !== base.origin || destination.pathname.startsWith("//")) return null;
    return `${destination.pathname}${destination.search}${destination.hash}`;
  } catch {
    return null;
  }
}
