import { defineStore } from "pinia";

export type JobsState = {
  currentCancelJobId: number | null;
  deleteJobId: number | null;
};

export const useJobsStore = defineStore("jobs", {
  state: (): JobsState => ({
    currentCancelJobId: null,
    deleteJobId: null
  }),

  actions: {
    cancelJob(jobId: number) {
      this.currentCancelJobId = jobId;
    },
    deleteJob(jobId: number) {
      this.deleteJobId = jobId;
    }
  }
});
