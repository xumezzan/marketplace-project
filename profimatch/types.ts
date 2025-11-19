export enum UserRole {
  CLIENT = 'CLIENT',
  SPECIALIST = 'SPECIALIST',
}

export interface Category {
  id: string;
  name: string;
  iconName: string;
  description: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  category: string;
  budgetMin?: number;
  budgetMax?: number;
  location: string;
  date: string;
  status: 'open' | 'in_progress' | 'completed';
  createdAt: Date;
}

export interface Review {
  id: string;
  author: string;
  rating: number;
  date: string;
  text: string;
}

export interface PortfolioItem {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
}

export interface Specialist {
  id: string;
  name: string;
  profession: string;
  rating: number;
  reviewsCount: number;
  avatarUrl: string;
  categories: string[];
  about: string;
  hourlyRate: number;
  reviews: Review[];
  portfolio: PortfolioItem[];
}

export interface AIAnalysisResult {
  suggestedTitle: string;
  suggestedCategory: string;
  refinedDescription: string;
  estimatedBudgetMin: number;
  estimatedBudgetMax: number;
}