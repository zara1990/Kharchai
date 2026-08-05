import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';

type Props = NativeStackScreenProps<
  RootStackParamList,
  'ProcessingPlaceholder'
>;

export default function ProcessingPlaceholderScreen({
  navigation,
  route,
}: Props) {
  const { capturedImages } = route.params;
  const imageCount = capturedImages.length;

  const handleDone = () => {
    navigation.popToTop();
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.icon}>🧾</Text>

        <Text style={styles.title}>Receipt Captured</Text>

        <Text style={styles.body}>
          AI-powered receipt analysis will be available in the next milestone.
          {'\n\n'}
          {imageCount === 1
            ? '1 image is ready to process.'
            : `${imageCount} images are ready to process.`}
        </Text>

        <View style={styles.infoBox}>
          <Text style={styles.infoText}>
            ⚡ Nothing has been uploaded. Your receipt stays on your device
            until you submit it in a future step.
          </Text>
        </View>

        <TouchableOpacity
          style={styles.doneButton}
          onPress={handleDone}
          activeOpacity={0.85}
        >
          <Text style={styles.doneButtonText}>Done</Text>
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

  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 32,
  },

  icon: {
    fontSize: 64,
    marginBottom: 24,
  },

  title: {
    fontSize: 24,
    fontWeight: '800',
    color: '#1A1A2E',
    marginBottom: 12,
    textAlign: 'center',
  },

  body: {
    fontSize: 15,
    color: '#555',
    lineHeight: 24,
    textAlign: 'center',
    marginBottom: 32,
  },

  infoBox: {
    backgroundColor: '#EDF7F0',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#A8D5B8',
    width: '100%',
    marginBottom: 24,
  },

  infoText: {
    color: '#1B5E3B',
    fontSize: 13,
    lineHeight: 20,
    textAlign: 'center',
  },

  doneButton: {
    backgroundColor: '#1B5E3B',
    width: '100%',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    elevation: 3,
  },

  doneButtonText: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '700',
  },
});