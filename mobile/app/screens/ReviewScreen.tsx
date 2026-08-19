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
  ActivityIndicator,
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { UFRItem, UniversalFinancialRecord } from '../types/ufr';
import {
  saveFinancialRecord,
  SaveError,
  SaveRecordPayload,
} from '../services/documentService';
import SectionTitle from '../components/review/SectionTitle';
import DetailRow from '../components/review/DetailRow';
import ItemRow from '../components/review/ItemRow';
import HintCard from '../components/review/HintCard';
import { generateUUID } from '../utils/uuid';

type Props = NativeStackScreenProps<RootStackParamList, 'Review'>;

const { height: SH } = Dimensions.get('window');

// ── Amount / currency helpers ─────────────────────────────────────────────────

/** Parse a numeric amount from a formatted string such as "PKR 2,450" → 2450. */
function parseNumericAmount(s: string): number | null {
  const cleaned = s.replace(/[^0-9.]/g, '');
  if (!cleaned) return null;
  const n = parseFloat(cleaned);
  return isNaN(n) ? null : n;
}

/** Extract a 2-4 letter ISO currency code from a formatted string such as "PKR 2,450" → "PKR". */
function parseCurrencyCode(s: string): string | null {
  const match = s.match(/\b([A-Z]{2,4})\b/);
  return match ? match[1] : null;
}

// ── UFR payload builder ───────────────────────────────────────────────────────

function buildSavePayload(
  recordId: string,
  editedMerchant: string,
  editedDate: string,
  editedTotal: string,
  editedItems: UFRItem[],
  ufr: UniversalFinancialRecord,
  confirmTotalMismatch: boolean = false,
): SaveRecordPayload {
  return {
    record_id: recordId,
    document_type: ufr.documentType,
    merchant: editedMerchant.trim() || null,
    document_date: editedDate.trim() || null,
    currency: parseCurrencyCode(editedTotal),
    total_amount: parseNumericAmount(editedTotal),
    payment_method: null,
    category: null,
    items: editedItems.map((item) => ({
      description: item.name,
      amount: parseNumericAmount(item.amount),
      quantity: null,
      unit_price: null,
      category: null,
      metadata: {},
    })),
    metadata: {
      source: 'receipt_analysis',
      confidence: null,
      confidence_level: ufr.confidence || null,
      review_required: null,
      review_hints: ufr.reviewHints.map((hint) => ({
        field: 'general',
        message: hint,
      })),
      quality_score: null,
      parser_version: 'mobile-review-v1',
      service_charge: parseNumericAmount(ufr.serviceCharge ?? ''),
      tax_amount: parseNumericAmount(ufr.taxAmount ?? ''),
      delivery_charge: parseNumericAmount(ufr.deliveryCharge ?? ''),
      discount_amount: parseNumericAmount(ufr.discountAmount ?? ''),
      subtotal_amount: parseNumericAmount(ufr.subtotalAmount ?? ''),
      confirm_total_mismatch: confirmTotalMismatch || undefined,
    },
  };
}

// ── Screen ────────────────────────────────────────────────────────────────────

export default function ReviewScreen({ route, navigation }: Props) {
  const { imageUri, ufr: uploadedUfr } = route.params;
  const [ufr, setUfr] = useState<UniversalFinancialRecord | null>(null);

  // Editable local state — initialized from UFR when it loads.
  const [editedMerchant, setEditedMerchant] = useState('');
  const [editedDate, setEditedDate] = useState('');
  const [editedTotal, setEditedTotal] = useState('');
  const [editedItems, setEditedItems] = useState<UFRItem[]>([]);

  // Save lifecycle state.
  const [isSaving, setIsSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  // Stable record ID — generated once when the UFR loads; reused on retry.
  const [recordId, setRecordId] = useState<string | null>(null);

  useEffect(() => {
    setUfr(uploadedUfr);
    setEditedMerchant(uploadedUfr.merchant);
    setEditedDate(uploadedUfr.date);
    setEditedTotal(uploadedUfr.total);
    setEditedItems(uploadedUfr.items);
    // Generate the record ID once; it does not change across save retries.
    setRecordId(generateUUID());
  }, [uploadedUfr]);

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

  const doSave = async (confirmMismatch: boolean) => {
    if (isSaving || saved || !ufr || !recordId) return;

    const payload = buildSavePayload(
      recordId,
      editedMerchant,
      editedDate,
      editedTotal,
      editedItems,
      ufr,
      confirmMismatch,
    );

    setIsSaving(true);

    try {
      await saveFinancialRecord(payload);

      // HTTP 201 — success.
      setSaved(true);
      Alert.alert(
        'Saved',
        'Your financial record has been saved successfully.',
        [{ text: 'OK', onPress: () => navigation.popToTop() }],
      );
    } catch (error) {
      if (error instanceof SaveError) {
        if (error.status === 409) {
          const body = error.body as {
            detail?: { error?: string; message?: string; record_id?: string };
          } | null;
          const errorCode = body?.detail?.error;

          if (errorCode === 'total_mismatch') {
            // Non-critical arithmetic mismatch — ask the user to confirm.
            Alert.alert(
              "Amounts don't fully match",
              "The item amounts do not fully reconcile with the final total. " +
                "This may be caused by GST, service charges, discounts, rounding, " +
                "or an extraction issue.",
              [
                {
                  text: 'Review Amounts',
                  style: 'cancel',
                  // Dismiss dialog; user stays on Review Screen to edit.
                },
                {
                  text: 'Save Anyway',
                  style: 'destructive',
                  onPress: () => doSave(true),
                },
              ],
            );
          } else if (errorCode === 'Financial record already exists') {
            // Duplicate — treat as already saved.
            setSaved(true);
            Alert.alert(
              'Already Saved',
              'This record has already been saved. No duplicate was created.',
              [{ text: 'OK', onPress: () => navigation.popToTop() }],
            );
          } else {
            Alert.alert(
              'Already Saved',
              'This record has already been saved. No duplicate was created.',
              [{ text: 'OK', onPress: () => navigation.popToTop() }],
            );
          }
        } else if (error.status === 422) {
          // Hard validation error — keep the user on the review screen with edits intact.
          const body = error.body as { detail?: { errors?: string[] } } | null;
          const details =
            body?.detail?.errors?.join('\n') ??
            'The record could not be validated. Please check your entries and try again.';
          Alert.alert('Validation Error', details);
        } else if (error.status === 503) {
          Alert.alert(
            'Temporarily Unavailable',
            'Saving is temporarily unavailable. Your edits are preserved — please try again shortly.',
          );
        } else {
          Alert.alert(
            'Save Failed',
            `An unexpected error occurred (HTTP ${error.status}). Your edits are preserved.`,
          );
        }
      } else {
        // Network / timeout error.
        Alert.alert(
          'Connection Error',
          (error as Error).message ||
            'Could not reach the server. Check your connection and try again.',
        );
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleSave = () => doSave(false);

  // Read-only values that are never edited.
  const documentType = ufr?.documentType ?? '';
  const confidence = ufr?.confidence ?? '';
  const reviewHints = ufr?.reviewHints ?? [];

  // Charges summary — show only when at least one field is non-empty.
  const hasCharges =
    ufr &&
    [
      ufr.subtotalAmount,
      ufr.taxAmount,
      ufr.serviceCharge,
      ufr.deliveryCharge,
      ufr.discountAmount,
    ].some((v) => v);

  const saveButtonDisabled = isSaving || saved || !ufr;

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

        {hasCharges && (
          <>
            <SectionTitle title="Charges & Total" />
            <View style={styles.card}>
              {ufr?.subtotalAmount ? (
                <DetailRow label="Subtotal" value={ufr.subtotalAmount} />
              ) : null}
              {ufr?.taxAmount ? (
                <DetailRow label="GST / Tax" value={ufr.taxAmount} />
              ) : null}
              {ufr?.serviceCharge ? (
                <DetailRow label="Service Charge" value={ufr.serviceCharge} />
              ) : null}
              {ufr?.deliveryCharge ? (
                <DetailRow label="Delivery Charge" value={ufr.deliveryCharge} />
              ) : null}
              {ufr?.discountAmount ? (
                <DetailRow label="Discount" value={`− ${ufr.discountAmount}`} />
              ) : null}
              <View style={styles.totalDivider} />
              <DetailRow label="Final Total" value={editedTotal} />
            </View>
          </>
        )}

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
          style={[
            styles.saveButton,
            saveButtonDisabled && styles.saveButtonDisabled,
          ]}
          activeOpacity={0.85}
          onPress={handleSave}
          disabled={saveButtonDisabled}
        >
          {isSaving ? (
            <ActivityIndicator color="#FFFFFF" size="small" />
          ) : (
            <Text style={styles.saveButtonText}>
              {saved ? 'Saved ✓' : 'Save'}
            </Text>
          )}
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
  totalDivider: {
    height: 1,
    backgroundColor: '#E8EDF2',
    marginVertical: 8,
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
  saveButtonDisabled: {
    opacity: 0.55,
    elevation: 0,
    shadowOpacity: 0,
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
});
