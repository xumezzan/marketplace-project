import { GoogleGenAI, Type } from "@google/genai";
import { AIAnalysisResult } from "../types";

const apiKey = process.env.API_KEY || '';

const ai = new GoogleGenAI({ apiKey });

export const analyzeTaskDescription = async (userInput: string, language: 'ru' | 'uz'): Promise<AIAnalysisResult | null> => {
  if (!apiKey) {
    console.error("API Key is missing");
    return null;
  }

  try {
    const langInstruction = language === 'uz' 
      ? 'Vazifani o\'zbek tilida tahlil qiling va javoblarni O\'ZBEK tilida qaytaring.' 
      : 'Проанализируй запрос пользователя и верни структурированные данные на РУССКОМ языке.';

    const prompt = `
      Ты помощник сервиса по поиску специалистов (Profi.ru, YouDo). 
      ${langInstruction}
      Пользователь хочет: "${userInput}".
      
      Предложи:
      1. Короткий и понятный заголовок задачи.
      2. Категорию услуги (например: Ремонт, Сантехника, Уборка, Репетиторы, Красота, Перевозки, IT).
      3. Улучшенное, профессиональное описание задачи.
      4. Оценочный диапазон бюджета (числа).
    `;

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            suggestedTitle: { type: Type.STRING },
            suggestedCategory: { type: Type.STRING },
            refinedDescription: { type: Type.STRING },
            estimatedBudgetMin: { type: Type.NUMBER },
            estimatedBudgetMax: { type: Type.NUMBER },
          },
          required: ["suggestedTitle", "suggestedCategory", "refinedDescription", "estimatedBudgetMin", "estimatedBudgetMax"],
        },
      },
    });

    const text = response.text;
    if (!text) return null;

    return JSON.parse(text) as AIAnalysisResult;
  } catch (error) {
    console.error("Error analyzing task with Gemini:", error);
    return null;
  }
};
