import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  StatusBar,
} from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';

type HomeScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Home'>;

interface Props {
  navigation: HomeScreenNavigationProp;
}

export default function HomeScreen({ navigation }: Props) {
  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" backgroundColor="#1B5E3B" />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.appName}>KharchAI</Text>
        <Text style={styles.tagline}>Your AI-powered financial copilot</Text>
      </View>

      {/* Main content */}
      <View style={styles.content}>
        <View style={styles.emptyState}>
          <Text style={styles.emptyStateIcon}>📊</Text>
          <Text style={styles.emptyStateTitle}>No expenses yet</Text>
          <Text style={styles.emptyStateText}>
            Your expenses will appear here once you start adding them.
            Track your spending in PKR with AI-powered receipt scanning.
          </Text>
        </View>
      </View>

      {/* Footer CTA */}
      <View style={styles.footer}>
        <TouchableOpacity
          style={styles.primaryButton}
          onPress={() => navigation.navigate('AddExpense')}
          activeOpacity={0.85}
        >
          <Text style={styles.primaryButtonText}>+ Add Expense</Text>
        </TouchableOpacity>
        <Text style={styles.footerNote}>Track your spending in PKR</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#1B5E3B',
  },
  header: {
    backgroundColor: '#1B5E3B',
    paddingHorizontal: 24,
    paddingTop: 32,
    paddingBottom: 36,
  },
  appName: {
    fontSize: 34,
    fontWeight: '800',
    color: '#FFFFFF',
    letterSpacing: 0.5,
  },
  tagline: {
    fontSize: 14,
    color: '#A8D5B8',
    marginTop: 4,
  },
  content: {
    flex: 1,
    backgroundColor: '#F8F9FA',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: 24,
    paddingTop: 40,
  },
  emptyState: {
    alignItems: 'center',
    paddingTop: 40,
  },
  emptyStateIcon: {
    fontSize: 60,
    marginBottom: 20,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1A1A2E',
    marginBottom: 10,
  },
  emptyStateText: {
    fontSize: 14,
    color: '#888888',
    textAlign: 'center',
    lineHeight: 22,
    paddingHorizontal: 16,
  },
  footer: {
    backgroundColor: '#F8F9FA',
    paddingHorizontal: 24,
    paddingBottom: 36,
    paddingTop: 16,
    alignItems: 'center',
  },
  primaryButton: {
    backgroundColor: '#1B5E3B',
    paddingVertical: 16,
    borderRadius: 12,
    width: '100%',
    alignItems: 'center',
    elevation: 3,
    shadowColor: '#1B5E3B',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  footerNote: {
    marginTop: 12,
    fontSize: 12,
    color: '#AAAAAA',
  },
});
