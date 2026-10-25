import { expect, jest, test } from '@jest/globals';
import { render, screen } from '@testing-library/react-native';

import { Button } from '../Button';

jest.mock('@expo/vector-icons', () => ({
  Feather: ({ name }: { name: string }) => {
    const React = jest.requireActual<typeof import('react')>('react');
    const { Text } = jest.requireActual<typeof import('react-native')>('react-native');
    return React.createElement(Text, null, `\uE000_${name}`);
  },
}));

test('a Button with an icon has exactly its title as its accessible name', () => {
  render(<Button title="Find my course" icon="search" onPress={jest.fn()} />);
  const button = screen.getByRole('button', { name: 'Find my course' });
  expect(button).toBeTruthy();
  expect(button.props.accessibilityLabel).toBe('Find my course');
});
