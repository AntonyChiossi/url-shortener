/**
 * @file common.ts
 * @author Antony Chiossi
 */

export interface Url {}
export interface UserUrls {
  urls: UrlInUserUrls[];
}

export interface UrlInUserUrls {
  short_id: string;
  short_url: string;
  long_url: string;
  expires_at?: string;
}

export interface UrlStats {
  expires_at: string;
  long_url: string;
  clicks: Click[];
  total_clicks: number;
}

export interface Click {
  user_agent: string;
  ip_address: string;
  referrer?: any;
  date: string;
}
