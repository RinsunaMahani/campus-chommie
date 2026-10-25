import { expect, jest, test } from '@jest/globals';
import { render, screen } from '@testing-library/react-native';
import { Dimensions, Text } from 'react-native';

import { PaletteProvider, night, paper } from '@/shared/theme/palette';
import { Screen } from '../Screen';

jest.mock('expo-router', () => ({
  router: { push: jest.fn(), back: jest.fn(), canGoBack: () => true, replace: jest.fn() },
}));
jest.mock('@expo/vector-icons', () => ({ Feather: () => null }));
jest.mock('react-native-safe-area-context', () => {
  const actual = jest.requireActual<typeof import('react-native-safe-area-context')>('react-native-safe-area-context');
  const React = jest.requireActual<typeof import('react')>('react');
  const rn = jest.requireActual<typeof import('react-native')>('react-native');
  return {
    ...actual,
    useSafeAreaInsets: () => ({ top: 20, left: 0, right: 0, bottom: 34 }),
    SafeAreaView: ({ children, edges, style }: { children: React.ReactNode; edges: string[]; style?: object }) =>
      React.createElement(
        rn.View,
        {
          testID: 'safe-area',
          accessibilityLabel: edges ? edges.join(',') : '',
          style,
        },
        children,
      ),
  };
});

test("a tab screen's hero band runs up under the status bar and takes the top inset itself", () => {
  render(
    <Screen
      tab
      hero
      title="Home"
      overline="Sunday, 25 October 2026"
      band={<Text>SMU · Sefako Makgatho Health Sciences University</Text>}>
      <Text>Content</Text>
    </Screen>,
  );

  // The photo fills the status bar's space: no top edge on the safe area (the band pads itself by the inset).
  const safeArea = screen.getByTestId('safe-area');
  expect(safeArea.props.accessibilityLabel).toBe('');
  expect(screen.getByText('Home')).toBeTruthy();
  expect(screen.getByText('SMU · Sefako Makgatho Health Sciences University')).toBeTruthy();
});

test('hero screen renders at 360 px and 412 px widths', () => {
  for (const width of [360, 412]) {
    jest.spyOn(Dimensions, 'get').mockReturnValue({ width, height: 800, scale: 2, fontScale: 1 });
    const { unmount } = render(
      <Screen
        tab
        hero
        title="Home"
        overline="Sunday, 25 October 2026"
        band={<Text>SMU · Sefako Makgatho Health Sciences University</Text>}>
        <Text>Content</Text>
      </Screen>,
    );
    expect(screen.getByText('Home')).toBeTruthy();
    expect(screen.getByText('SMU · Sefako Makgatho Health Sciences University')).toBeTruthy();
    unmount();
  }
});

test('hero screen renders in light and night themes at 360 and 412 px', () => {
  for (const palette of [paper, night]) {
    for (const width of [360, 412]) {
      jest.spyOn(Dimensions, 'get').mockReturnValue({ width, height: 800, scale: 2, fontScale: 1 });
      const { unmount } = render(
        <PaletteProvider palette={palette}>
          <Screen
            tab
            hero
            title="Home"
            overline="Sunday, 25 October 2026"
            band={<Text>SMU · Sefako Makgatho Health Sciences University</Text>}>
            <Text>Content</Text>
          </Screen>
        </PaletteProvider>,
      );
      expect(screen.getByText('Home')).toBeTruthy();
      expect(screen.getByText('SMU · Sefako Makgatho Health Sciences University')).toBeTruthy();
      unmount();
    }
  }
});
