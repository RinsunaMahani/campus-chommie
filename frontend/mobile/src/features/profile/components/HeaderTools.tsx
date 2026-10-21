/** What a student screen's header carries: the demo tag above the title (on a demo account, always in full),
 * and the Help button on the title's line. */
import { HelpButton } from '@/features/support/components/HelpButton';

import { DemoBanner } from './DemoBanner';

/** Pass as a Screen's headerRight and titleAside: {...studentHeader()}. */
export function studentHeader(help = true) {
  return { headerRight: <DemoBanner />, titleAside: help ? <HelpButton /> : undefined };
}
