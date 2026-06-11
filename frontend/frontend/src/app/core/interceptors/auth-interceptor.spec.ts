import { vi } from 'vitest';
import { HttpRequest } from '@angular/common/http';
import { of } from 'rxjs';

import { authInterceptor } from './auth-interceptor';

describe('authInterceptor', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should add an authorization header when a token exists', () => {
    localStorage.setItem('token', 'test-token');

    const request = new HttpRequest('GET', '/api/test');
    const next = vi.fn().mockReturnValue(of({}));

    authInterceptor(request, next);

    const forwardedRequest = next.mock.calls[0][0] as HttpRequest<unknown>;
    expect(forwardedRequest.headers.get('Authorization'))
      .toBe('Bearer test-token');
  });

  it('should forward the request unchanged without a token', () => {
    const request = new HttpRequest('GET', '/api/test');
    const next = vi.fn().mockReturnValue(of({}));

    authInterceptor(request, next);

    expect(next.mock.calls[0][0]).toBe(request);
  });
});
