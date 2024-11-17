import * as reactRouterDom from 'react-router-dom';
import { vi } from 'vitest';

// use to mock useMediaQuery
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn()
  }))
});

// mock react-router-dom
vi.mock('react-router-dom', async () => {
  const reactRouterDomImports: object = await vi.importActual('react-router-dom');
  return {
    ...reactRouterDomImports,
    useNavigate: vi.fn(),
    useLocation: () => ({ pathname: '/' })
  };
});

vi.mock('utils/openNotification', () => ({
  default: vi.fn()
}));

vi.mock('hooks/useIntersectionObserver', () => ({
  default: vi.fn()
}));

vi.stubEnv('VITE_BACKEND_API_BASE_URL', 'http://localhost:8000/');
vi.stubEnv('VITE_ENV', 'dev');

const dummyNavigate = vi.fn();
const useNavigateMock = vi.spyOn(reactRouterDom, 'useNavigate');
useNavigateMock.mockReturnValue(dummyNavigate);
