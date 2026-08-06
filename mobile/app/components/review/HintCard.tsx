import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

type Props = {
  hint: string;
};

export default function HintCard({ hint }: Props) {
  return (
    <View style={styles.hintCard}>
      <Text style={styles.hintText}>✓  {hint}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  hintCard: {
    backgroundColor: '#EDF7F0',
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: '#A8D5B8',
  },
  hintText: {
    fontSize: 14,
    color: '#1B5E3B',
    lineHeight: 20,
  },
});
