/**
 * "Is this college registered?": a name or DHET registration number, checked against DHET's registers
 * and its list of bogus colleges. The answer in words, every institution it matched (most serious
 * first), DHET's warning signs, and which registers it was checked against. "Not found" never says
 * "bogus". Nothing typed here is stored.
 */
import { useState } from 'react';
import { StyleSheet, Text, TextInput, View } from 'react-native';

import { errorText } from '@/features/courseFinder/words';
import { Button } from '@/shared/components/Button';
import { HeroScreen } from '@/shared/components/HeroScreen';
import { Card, Tag } from '@/shared/components/Parts';
import { SourceLink } from '@/shared/components/SourceLink';
import { ErrorBox } from '@/shared/components/Status';
import { Muted, Overline, Strong } from '@/shared/components/Text';
import { t } from '@/shared/i18n';
import { FadeIn } from '@/shared/motion/FadeIn';
import { Palette, usePalette, useStyles } from '@/shared/theme/palette';
import { fonts, radius } from '@/shared/theme/tokens';

import { collegesApi } from '../api/collegesApi';
import { CollegeRow, statusTone } from '../CollegeRow';
import { CheckAnswer } from '../types';
import { Signs } from './CollegeScreen';

const MIN_CHARS = 3;

export default function CheckCollegeScreen() {
  const colors = usePalette();
  const styles = useStyles(makeStyles);
  const [name, setName] = useState('');
  const [answer, setAnswer] = useState<CheckAnswer | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const ready = name.trim().length >= MIN_CHARS;

  async function check() {
    if (!ready) return;
    setBusy(true);
    setError(null);
    try {
      setAnswer(await collegesApi.check(name.trim()));
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <HeroScreen back title={t('colleges.checkTitle')} subtitle={t('colleges.checkSub')}>
      <TextInput
        value={name}
        onChangeText={setName}
        onSubmitEditing={check}
        placeholder={t('colleges.checkLabel')}
        placeholderTextColor={colors.textFaint}
        accessibilityLabel={t('colleges.checkLabel')}
        autoCorrect={false}
        maxLength={120}
        returnKeyType="search"
        style={styles.input}
      />
      {name.trim().length > 0 && !ready ? <Muted>{t('colleges.searchHint')}</Muted> : null}
      <Button title={t('colleges.checkButton')} variant="accent" icon="shield" onPress={check} disabled={!ready || busy} />

      {error ? <ErrorBox message={error} /> : null}

      {answer ? (
        <FadeIn style={{ gap: 14 }}>
          <Card style={styles.card}>
            <Tag label={answer.label} tone={statusTone(answer.verdict)} />
            {answer.lines.map((line, i) => (
              <Text key={i} style={styles.line}>
                {line}
              </Text>
            ))}
          </Card>

          {answer.colleges.length || answer.unregistered.length ? <Overline>{t('colleges.matches')}</Overline> : null}
          {answer.unregistered.map((u) => (
            <Card key={u.id} style={styles.card}>
              <View style={styles.head}>
                <Strong style={styles.name}>{u.name}</Strong>
                <Tag label={u.label} tone="garnet" />
              </View>
              {u.where ? <Muted>{t('colleges.bogusWhere', { where: u.where })}</Muted> : null}
            </Card>
          ))}
          {answer.colleges.map((c) => (
            <CollegeRow key={c.id} college={c} />
          ))}

          {answer.warning_signs ? <Signs signs={answer.warning_signs} /> : null}

          <Card style={styles.card}>
            <Overline>{t('colleges.checkedAgainst')}</Overline>
            {answer.sources.map((s) => (
              <View key={s.url} style={{ gap: 2 }}>
                <Muted>{s.title ?? s.publisher}</Muted>
                <SourceLink url={s.url} />
              </View>
            ))}
          </Card>
        </FadeIn>
      ) : null}
    </HeroScreen>
  );
}

const makeStyles = (colors: Palette) =>
  StyleSheet.create({
  input: {
    height: 50,
    paddingHorizontal: 14,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.white,
    fontFamily: fonts.medium,
    fontSize: 16,
    color: colors.text,
  },
  card: { gap: 10, padding: 14 },
  head: { flexDirection: 'row', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 },
  name: { flex: 1, fontSize: 15.5, color: colors.text },
  line: { fontFamily: fonts.body, fontSize: 15, lineHeight: 21, color: colors.text },
});
