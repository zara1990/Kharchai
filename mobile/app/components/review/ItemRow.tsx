import React from 'react';
import { View, Text, TextInput, StyleSheet } from 'react-native';

type Props = {
  name: string;
  amount: string;
  onChangeName?: (text: string) => void;
  onChangeAmount?: (text: string) => void;
};

export default function ItemRow({ name, amount, onChangeName, onChangeAmount }: Props) {
  return (
    <View style={styles.itemRow}>
      {onChangeName ? (
        <TextInput
          style={styles.itemNameInput}
          value={name}
          onChangeText={onChangeName}
          underlineColorAndroid="transparent"
        />
      ) : (
        <Text style={styles.itemName}>{name}</Text>
      )}
      <View style={styles.itemDots} />
      {onChangeAmount ? (
        <TextInput
          style={styles.itemAmountInput}
          value={amount}
          onChangeText={onChangeAmount}
          underlineColorAndroid="transparent"
        />
      ) : (
        <Text style={styles.itemAmount}>{amount}</Text>
      )}
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
  itemNameInput: {
    fontSize: 14,
    color: '#1A1A2E',
    borderBottomWidth: 1,
    borderBottomColor: '#1B5E3B',
    paddingVertical: 0,
    paddingHorizontal: 0,
    minWidth: 80,
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
  itemAmountInput: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1A1A2E',
    borderBottomWidth: 1,
    borderBottomColor: '#1B5E3B',
    paddingVertical: 0,
    paddingHorizontal: 0,
    minWidth: 70,
    textAlign: 'right',
  },
});
