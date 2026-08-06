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
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { UniversalFinancialRecord } from '../types/ufr';
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

  useEffect(() => {
    let cancelled = false;

    uploadDocument(capturedImages).then((result) => {
      if (!cancelled) {
        setUfr(result);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [capturedImages]);

  const { documentType, merchant, date, total, items, confidence, reviewHints } =
    ufr ?? {
      documentType: '',
      merchant: '',
      date: '',
      total: '',
      items: [],
      confidence: '',
      reviewHints: [],
    };

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
          <DetailRow label="Merchant" value={merchant} />
          <DetailRow label="Date" value={date} />
          <DetailRow label="Total" value={total} />
        </View>

        <SectionTitle title="Items" />
        <View style={styles.card}>
          {items.map((item) => (
            <ItemRow key={item.name} name={item.name} amount={item.amount} />
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
        <TouchableOpacity style={styles.saveButton} activeOpacity={0.85}>
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
