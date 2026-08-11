import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  Image,
  StyleSheet,
  SafeAreaView,
  Dimensions,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { UFRItem, UniversalFinancialRecord } from '../types/ufr';
import { uploadDocument } from '../services/documentService';
import SectionTitle from '../components/review/SectionTitle';
import DetailRow from '../components/review/DetailRow';
import ItemRow from '../components/review/ItemRow';
import HintCard from '../components/review/HintCard';

type Props = NativeStackScreenProps<RootStackParamList, 'Review'>;

const { height: SH } = Dimensions.get('window');

export default function ReviewScreen({ route }: Props) {
  const { imageUri, capturedImages } = route.params;
  const [ufr, setUfr] = useState<UniversalFinancialRecord | null>(null);

  // Editable local state — initialized from UFR when it loads.
  const [editedMerchant, setEditedMerchant] = useState('');
  const [editedDate, setEditedDate] = useState('');
  const [editedTotal, setEditedTotal] = useState('');
  const [editedItems, setEditedItems] = useState<UFRItem[]>([]);

  useEffect(() => {
    let cancelled = false;

    uploadDocument(capturedImages).then((result) => {
      if (!cancelled) {
        setUfr(result);
        setEditedMerchant(result.merchant);
        setEditedDate(result.date);
        setEditedTotal(result.total);
        setEditedItems(result.items);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [capturedImages]);

  const updateItemName = (index: number, text: string) => {
    setEditedItems((prev) =>
      prev.map((item, i) => (i === index ? { ...item, name: text } : item)),
    );
  };

  const updateItemAmount = (index: number, text: string) => {
    setEditedItems((prev) =>
      prev.map((item, i) => (i === index ? { ...item, amount: text } : item)),
    );
  };

  const handleSave = () => {
    const editedUFR: UniversalFinancialRecord = {
      documentType: ufr?.documentType ?? '',
      merchant: editedMerchant,
      date: editedDate,
      total: editedTotal,
      items: editedItems,
      confidence: ufr?.confidence ?? '',
      reviewHints: ufr?.reviewHints ?? [],
    };
    console.log('Edited UFR:', JSON.stringify(editedUFR, null, 2));
    Alert.alert('Expense ready to save');
  };

  // Read-only values that are never edited.
  const documentType = ufr?.documentType ?? '';
  const confidence = ufr?.confidence ?? '';
  const reviewHints = ufr?.reviewHints ?? [];

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.imageWrapper}>
        <Image
          source={{ uri: imageUri }}
          style={styles.image}
          resizeMode="contain"
        />
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <SectionTitle title="Document Details" />
        <View style={styles.card}>
          <DetailRow label="Document Type" value={documentType} />
          <DetailRow
            label="Merchant"
            value={editedMerchant}
            editable
            onChangeText={setEditedMerchant}
          />
          <DetailRow
            label="Date"
            value={editedDate}
            editable
            onChangeText={setEditedDate}
          />
          <DetailRow
            label="Total"
            value={editedTotal}
            editable
            onChangeText={setEditedTotal}
          />
        </View>

        <SectionTitle title="Items" />
        <View style={styles.card}>
          {editedItems.map((item, index) => (
            <ItemRow
              key={index}
              name={item.name}
              amount={item.amount}
              onChangeName={(text) => updateItemName(index, text)}
              onChangeAmount={(text) => updateItemAmount(index, text)}
            />
          ))}
        </View>

        <SectionTitle title="Confidence" />
        <View style={styles.confidenceBadge}>
          <Text style={styles.confidenceText}>{confidence}</Text>
        </View>

        <SectionTitle title="Review Hints" />
        <View style={styles.hintsSection}>
          {reviewHints.map((hint) => (
            <HintCard key={hint} hint={hint} />
          ))}
        </View>
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity
          style={styles.saveButton}
          activeOpacity={0.85}
          onPress={handleSave}
        >
          <Text style={styles.saveButtonText}>Save</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  imageWrapper: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 8,
  },
  image: {
    width: '100%',
    height: SH * 0.35,
    borderRadius: 12,
    backgroundColor: '#E8EDF2',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 24,
    paddingTop: 8,
    paddingBottom: 16,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E8EDF2',
  },
  confidenceBadge: {
    alignSelf: 'flex-start',
    backgroundColor: '#1B5E3B',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  confidenceText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  hintsSection: {
    gap: 8,
  },
  footer: {
    paddingHorizontal: 24,
    paddingTop: 12,
    paddingBottom: 24,
    backgroundColor: '#F8F9FA',
    borderTopWidth: 1,
    borderTopColor: '#E8EDF2',
  },
  saveButton: {
    backgroundColor: '#1B5E3B',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    elevation: 3,
    shadowColor: '#1B5E3B',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
});
