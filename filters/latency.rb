def filter(event)
    unsorted_owds = event.get('[result][histogram-latency]')
    owds=Hash[unsorted_owds.sort]
    c = 0
    sum = 0
    owds.each do |key, value|
        kv = key.to_f
        c += value
        sum = sum + kv * value
    end
    
    if c>0

        mean=sum/c
        res=0
        owds.each do |key, value|
            res += value * (key.to_f-mean) ** 2
        end
        sd = Math.sqrt(res/c)

        co=0
        med=0
        c = c/2
        owds.each do |key, value|
            kv = key.to_f
            co += value
            med = kv
            break if co>c
        end

    else
        mean = 0
        sd = 0
        med = 0
    end

    event.set('delay_mean', mean)
    event.set('delay_median', med)
    event.set('delay_sd', sd)
    return [event]
end