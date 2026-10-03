import { post } from "./api";

/** Javob yuborish; serverdan kelgan to'g'ri javob va izoh savolga yoziladi. */
export async function submitAnswer(attempt, questionId, answerId) {
  const res = await post(`/attempts/${attempt.id}/answer.bin`, { question: questionId, answer: answerId });
  const questions = attempt.questions.map((q) =>
    q.id === questionId
      ? {
          ...q,
          chosen: answerId,
          correct: res.correct_answer,
          explanation: res.explanation,
          photo_hint: res.photo_hint,
          audio_hint: res.audio_hint,
        }
      : q,
  );
  return { ...attempt, questions, finished: res.finished, result: res.result || attempt.result };
}
