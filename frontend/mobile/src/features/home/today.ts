/**
 * What Home's "Today" tiles say, worked out from what the student already has: their timetable, their classes'
 * tests and deadlines, and how long their money lasts. Pure, so it's tested without a screen. Times are SAST.
 */
import { TimetableEntry } from '@/features/timetable/types';
import { ClassEvent } from '@/features/week/types';

/** Now in South Africa (SAST is UTC+2 all year): the date, the weekday (0 = Monday) and minutes after midnight. */
export function nowInSast(at: Date = new Date()): { date: string; weekday: number; minutes: number } {
  const sast = new Date(at.getTime() + 2 * 60 * 60 * 1000);
  return {
    date: sast.toISOString().slice(0, 10),
    weekday: (sast.getUTCDay() + 6) % 7,
    minutes: sast.getUTCHours() * 60 + sast.getUTCMinutes(),
  };
}

const minutesOf = (hhmm: string) => Number(hhmm.slice(0, 2)) * 60 + Number(hhmm.slice(3, 5));

/** The class on now, or the next one this week (wrapping to next week), and in how many days. */
export function nextClass(entries: TimetableEntry[], now: { weekday: number; minutes: number }) {
  if (!entries.length) return null;
  for (let ahead = 0; ahead < 8; ahead++) {
    const day = (now.weekday + ahead) % 7;
    const today = entries
      .filter((e) => e.weekday === day && (ahead > 0 || minutesOf(e.ends) > now.minutes))
      .sort((a, b) => a.starts.localeCompare(b.starts));
    if (today.length) {
      const e = today[0];
      return { entry: e, daysAhead: ahead, now: ahead === 0 && minutesOf(e.starts) <= now.minutes };
    }
  }
  return null;
}

function daysBetween(from: string, to: string): number {
  return Math.round((Date.parse(`${to}T00:00:00Z`) - Date.parse(`${from}T00:00:00Z`)) / 86400000);
}

/** The next test or deadline that isn't cancelled or already past, and how many days away. */
export function nextDeadline(events: ClassEvent[], today: string, minutes: number) {
  const ahead = events
    .filter((e) => !e.cancelled && (e.on > today || (e.on === today && (!e.at || minutesOf(e.at) >= minutes))))
    .sort((a, b) => a.on.localeCompare(b.on) || (a.at ?? '23:59').localeCompare(b.at ?? '23:59'));
  return ahead.length ? { event: ahead[0], days: daysBetween(today, ahead[0].on) } : null;
}
