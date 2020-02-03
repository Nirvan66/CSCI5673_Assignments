struct timetuple {
        int hours;
        int minutes;
        int seconds;
        long int u_seconds;
};

program TIME_PROG {
        version TIME_VERS {
                timetuple TIME() = 1;
        } = 1;
} = 0x23451111;