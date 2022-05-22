def filter(event)
    owds = event.get('[result][histogram-latency]')
    c = 0
    sum = 0
    med_key=0
    med_val=0
    owds.each do |key, value|
        kv = key.to_f
        c = c + value
        sum = sum + kv * value
        if value > med_val
            med_val = value
            med_key = kv
        end
    end
    if c>0
        mean=sum/c
        res=0
        owds.each do |key, value|
            res = res + key.to_f * (value-mean) ** 2
        end
        sd = Math.sqrt(res/c)
    else
        mean=0
        sd=0
    end
    event.set('delay_mean', mean)
    event.set('delay_median', med_key)
    event.set('delay_sd', sd)
    return [event]
end