import React from 'react';
import { Text, StyleSheet } from 'react-native';

type Props = {
  title: string;
};

export default function SectionTitle({ title }: Props) {
  return <Text style={styles.sectionTitle}>{title}</Text>;
}

const styles = StyleSheet.create({
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1A1A2E',
    marginBottom: 10,
    marginTop: 16,
  },
});
