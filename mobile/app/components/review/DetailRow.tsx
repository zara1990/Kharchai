import React from 'react';
import { View, Text, TextInput, StyleSheet } from 'react-native';

type Props = {
  label: string;
  value: string;
  editable?: boolean;
  onChangeText?: (text: string) => void;
};

export default function DetailRow({ label, value, editable = false, onChangeText }: Props) {
  return (
    <View style={styles.detailRow}>
      <Text style={styles.detailLabel}>{label}</Text>
      {editable ? (
        <TextInput
          style={styles.detailInput}
          value={value}
          onChangeText={onChangeText}
          underlineColorAndroid="transparent"
        />
      ) : (
        <Text style={styles.detailValue}>{value}</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F3F6',
  },
  detailLabel: {
    fontSize: 14,
    color: '#666666',
    flex: 1,
  },
  detailValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1A1A2E',
    flex: 1.2,
    textAlign: 'right',
  },
  detailInput: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1A1A2E',
    flex: 1.2,
    textAlign: 'right',
    borderBottomWidth: 1,
    borderBottomColor: '#1B5E3B',
    paddingVertical: 0,
    paddingHorizontal: 0,
  },
});
