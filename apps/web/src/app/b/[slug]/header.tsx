import Link from "next/link";
import s from "./page.module.css";

export function Header() {
  return (
    <header className={s.top}>
      <Link href="/" className={s.brand}>mesa</Link>
      <Link href="/mis-tarjetas" className={s.account} aria-label="Mis tarjetas">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
          <circle cx="12" cy="8" r="4" />
          <path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6" strokeLinecap="round" />
        </svg>
      </Link>
    </header>
  );
}
