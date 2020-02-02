struct timetuple {
        int hours;
        int minutes;
        int seconds;
};

program TIME_PROG {
        version TIME_VERS {
                timetuple TIME() = 1;
        } = 1;
} = 0x23451111;