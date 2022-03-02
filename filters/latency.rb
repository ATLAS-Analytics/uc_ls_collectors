def filter(event)
    # event.set('message', "Hello, from Ruby! Message: #{event.get('message')}")
    owds=event.get('evenresult').get('histogram-latency')
    c=0
    sum=0
    event.each do |key, value|
        c=c+value
        sum=sum+key.to_f*value
    end
    event.set('owd',sum/c)
    # puts c, sum, sum/c
    return [event]
end