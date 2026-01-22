import delay from "./api";

export const analyzeProblem = async (problem) => {

  await delay(1000); // simulate backend processing

  // Fake generated report id
  return {
    reportId: Math.floor(Math.random() * 1000)
  };
};
