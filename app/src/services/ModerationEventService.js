class ModerationEventService {
  constructor() {
    this.observers = new Set();
  }

  subscribe(observer) {
    this.observers.add(observer);

    
    return () => {
      this.observers.delete(observer);
    };
  }

  notify(event) {
    this.observers.forEach((observer) => {
      observer(event);
    });
  }
}

const moderationEventService = new ModerationEventService();

export default moderationEventService;

