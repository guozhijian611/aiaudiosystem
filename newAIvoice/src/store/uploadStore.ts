// stores/uploadStore.ts
import { defineStore } from 'pinia';

export const useUploadStore = defineStore('upload', {
  state: () => ({
    files: [] as File[],
  }),
  actions: {
    setFiles(files: File[]) {
      this.files = files;
    },
    clearFiles() {
      this.files = [];
    },
  },
});
