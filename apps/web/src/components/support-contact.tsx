// NEXT_PUBLIC values are included in the browser bundle at build time.
const configuredEmail = process.env.NEXT_PUBLIC_SUPPORT_EMAIL?.trim() ?? "";
const parts = configuredEmail.split("@");
const local = parts[0] ?? "";
const domain = parts[1] ?? "";
const valid = parts.length === 2 && configuredEmail.length <= 254 && local.length <= 64
  && !local.startsWith(".") && !local.endsWith(".") && !local.includes("..")
  && /^[^\s<>"(),:;@\[\]\\\u0000-\u001f\u007f]+$/.test(local)
  && /^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$/i.test(domain);

/** A support address is shown only after the operator supplies a valid contact. */
export function SupportContact() {
  if (!valid) return <>Contacta al equipo que activó el programa.</>;
  return <>Soporte: <a href={`mailto:${encodeURIComponent(local)}@${domain}`}>{configuredEmail}</a></>;
}
