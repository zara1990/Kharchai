import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

type Props = {
  name: string;
  amount: string;
};

export default function ItemRow({ name, amount }: Props) {
  return (
    <View style={styles.itemRow}>
      <Text style={styles.itemName}>{name}</Text>
      <View style={styles.itemDots} />
      <Text style={styles.itemAmount}>{amount}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  itemRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F3F6',
  },
  itemName: {
    fontSize: 14,
    color: '#1A1A2E',
  },
  itemDots: {
    flex: 1,
    borderBottomWidth: 1,
    borderBottomColor: '#DDDDDD',
    borderStyle: 'dotted',
    marginHorizontal: 8,
    marginBottom: 4,
  },
  itemAmount: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1A1A2E',
  },
});
