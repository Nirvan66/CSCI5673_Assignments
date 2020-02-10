struct timetuple {
        int hours;
        int minutes;
        float seconds;
};
struct serverTime{
    struct timetuple receive;
    struct timetuple send;
};

program TIME_PROG {
        version TIME_VERS {
                serverTime TIME() = 1;
        } = 1;
} = 0x23451111;