import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ActivityIndicator,
  Animated,
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { uploadDocument } from '../services/documentService';

type Props = NativeStackScreenProps<RootStackParamList, 'Processing'>;

const PROGRESS_MESSAGES = [
  'Uploading document...',
  'Checking image quality...',
  'Detecting document type...',
  'Extracting information...',
  'Preparing review...',
] as const;

const MESSAGE_INTERVAL_MS = 1750;

export default function ProcessingScreen({ navigation, route }: Props) {
  const { capturedImages } = route.params;
  const imageUri = capturedImages[0];

  const [messageIndex, setMessageIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const messageOpacity = useRef(new Animated.Value(1)).current;
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  // Cycle progress messages while processing
  useEffect(() => {
    const interval = setInterval(() => {
      Animated.timing(messageOpacity, {
        toValue: 0,
        duration: 200,
        useNativeDriver: true,
      }).start(() => {
        setMessageIndex((prev) => (prev + 1) % PROGRESS_MESSAGES.length);
        Animated.timing(messageOpacity, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }).start();
      });
    }, MESSAGE_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [messageOpacity]);

  // Upload document and navigate to Review on success
  useEffect(() => {
    let cancelled = false;

    uploadDocument(capturedImages)
      .then((ufr) => {
        if (cancelled || !mountedRef.current) return;
        navigation.replace('Review', { imageUri, capturedImages, ufr });
      })
      .catch(() => {
        if (cancelled || !mountedRef.current) return;
        setError('Something went wrong while processing your document. Please try again.');
      });

    return () => {
      cancelled = true;
    };
  }, [capturedImages, imageUri, navigation]);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.brandName}>KharchAI</Text>
        <Text style={styles.tagline}>Your AI-powered financial copilot</Text>

        <View style={styles.loaderWrapper}>
          <ActivityIndicator size="large" color="#1B5E3B" />
        </View>

        <Animated.Text style={[styles.progressMessage, { opacity: messageOpacity }]}>
          {error ?? PROGRESS_MESSAGES[messageIndex]}
        </Animated.Text>

        {!error && (
          <Text style={styles.subtext}>This usually takes a few seconds</Text>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 32,
  },
  brandName: {
    fontSize: 28,
    fontWeight: '800',
    color: '#1B5E3B',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  tagline: {
    fontSize: 13,
    color: '#A8D5B8',
    marginBottom: 48,
  },
  loaderWrapper: {
    marginBottom: 32,
  },
  progressMessage: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1A1A2E',
    textAlign: 'center',
    minHeight: 24,
  },
  subtext: {
    fontSize: 13,
    color: '#888888',
    marginTop: 12,
    textAlign: 'center',
  },
});
