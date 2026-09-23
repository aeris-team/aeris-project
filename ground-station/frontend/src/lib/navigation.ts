import type { NavigateFunction } from 'react-router-dom';

let navigateFn: NavigateFunction | null = null;

export function setNavigator(fn: NavigateFunction) {
  navigateFn = fn;
}

export function navigateToTab(tab: string) {
  const path = tab === 'dashboard' ? '/' : `/${tab}`;
  navigateFn?.(path);
}

export function tabFromPath(pathname: string): string {
  const path = pathname.replace(/\/+$/, '') || '/';
  if (path === '/') return 'dashboard';
  return path.slice(1);
}
